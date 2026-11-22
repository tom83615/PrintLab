"""Session-independent prepared-print control. No scheduling or automatic retries."""
from __future__ import annotations
import datetime as dt
import hashlib
import re
import secrets
import threading
from . import core, prepared, bambuddy

TTL = 120
TERMINAL = {'blocked', 'observed', 'submitted', 'unknown'}

def _base():
    return core.ROOT / 'Runtime/workbench'

def _stamp_age(stamp):
    try:
        return (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(stamp)).total_seconds()
    except (TypeError, ValueError):
        return float('inf')

def recover_operations():
    """On service boot, never resume a worker or replay an external action."""
    with core.lock('workbench-start'):
        for path in (_base() / 'operations').glob('*.json'):
            op = core.read_json(path)
            if op.get('state') in {'checking', 'dispatching'}:
                op.update(state='unknown' if op['state'] == 'dispatching' else 'blocked',
                    message='服務曾重啟；發送結果需核對，不會重發' if op['state'] == 'dispatching' else '核驗被服務重啟中斷，未發送；可重新核驗',
                    updated_at=core.now())
                core.write_json(path, op)

def latest_operation(pid, jid):
    rows = [core.read_json(f) for f in (_base() / 'operations').glob('*.json')]
    rows = [x for x in rows if (x.get('project_id'), x.get('job_id')) == (pid, jid)]
    return _public(max(rows, key=lambda x: x['created_at'])) if rows else None

def capability(report):
    kind = report.get('transport', {}).get('kind')
    if kind == 'bambuddy_queue':
        from . import queue_sender
        return queue_sender.capability(report)
    if kind == 'bambu_studio':
        try:
            from . import studio_bridge
            result = studio_bridge.capability(report.get('project_id'), report.get('job_id'))
            result.pop('observation', None)
            return result
        except (ImportError, AttributeError):
            return {'available': False, 'kind': kind, 'message': '官方 Studio 獨立發送腳本尚未驗證，當前只能保存和核驗待打印件'}
    # Keep native mode changes out of this feature; a new transport needs its own review.
    return {'available': False, 'kind': kind, 'message': '這個打印包尚未準備獨立發送通道'}

def check(pid, jid, *, owner=None):
    if owner:
        with core.lock('workbench-start'):
            return _check(pid, jid, owner)
    return _check(pid, jid, None)

def _check(pid, jid, owner):
    result = prepared.check(pid, jid)
    transport = capability(result)
    result['transport'].update(transport)
    result['checks'].append({'id': 'sender', 'label': '獨立發送通道',
        'status': 'pass' if transport.get('available') is True else 'blocked', 'message': transport['message']})
    result['blockers'] = [x for x in result['checks'] if x['status'] == 'blocked']
    result['ready'] = not result['blockers']
    if result['ready'] and owner:
        token = secrets.token_urlsafe(32)
        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=TTL)
        ticket = {'project_id': result['project_id'], 'job_id': jid, 'fingerprint': result['fingerprint'],
                  'created_at': core.now(), 'owner': owner, 'consumed': False}
        core.write_json(_base() / 'checks' / (hashlib.sha256(token.encode()).hexdigest() + '.json'), ticket)
        result.update(check_token=token, expires_at=expires.isoformat())
    return result

def _operation_path(opid):
    if not re.fullmatch(r'[a-f0-9]{32}', opid):
        raise core.WorkflowError('操作編號無效')
    return _base() / 'operations' / (opid + '.json')

def _public(value):
    return {k: v for k, v in value.items() if k not in {'owner', 'request_id'}}

def operation(opid, owner):
    value = core.read_json(_operation_path(opid))
    if not value:
        raise core.WorkflowError('沒有找到工作台打印操作')
    return _public(value)

def reconcile_operation(opid, owner):
    """Read device evidence only; never retry a send or clear an unknown by guess."""
    path = _operation_path(opid)
    with core.lock('workbench-start'):
        op = core.read_json(path)
        if not op:
            raise core.WorkflowError('沒有找到工作台打印操作')
        if op.get('state') not in {'unknown', 'submitted', 'observed'}:
            return _public(op)
        jd = core.job_path(op['project_id'], op['job_id'])
        if (jd / 'dispatch.json').exists():
            try:
                observed = bambuddy.reconcile(op['project_id'], op['job_id'])
                op['observation'] = {k: observed.get(k) for k in ('matching_task', 'fresh', 'device_state')}
                if observed.get('matching_task') and observed.get('fresh'):
                    op.update(state='observed', message='設備已讀回匹配任務；首層與實物仍需檢查')
                else:
                    op['message'] = '尚未匹配到這次任務，保留原記錄；不會重複發送'
            except Exception:
                op['message'] = '暫時無法核對設備，保留原記錄；不會重複發送'
        op['updated_at'] = core.now()
        core.write_json(path, op)
        return _public(op)

def start(pid, jid, *, owner, check_token, plate_clear, request_id, launch=None):
    if not re.fullmatch(r'[a-zA-Z0-9_-]{20,100}', check_token or '') or not re.fullmatch(r'[a-fA-F0-9-]{32,36}', request_id or ''):
        raise core.WorkflowError('確認信息無效，請重新核驗')
    token_path = _base() / 'checks' / (hashlib.sha256(check_token.encode()).hexdigest() + '.json')
    with core.lock('workbench-start'):
        for file in (_base() / 'operations').glob('*.json'):
            op = core.read_json(file)
            if op.get('owner') == owner and op.get('request_id') == request_id:
                if (op['project_id'], op['job_id']) != (pid, jid):
                    raise core.WorkflowError('此確認已綁定另一任務')
                return _public(op)
            if op.get('state') not in TERMINAL or op.get('state') == 'unknown':
                raise core.WorkflowError('已有發送正在處理或結果不明，請先核對結果，不能重複發送')
        ticket = core.read_json(token_path)
        if (not ticket or ticket.get('owner') != owner or ticket.get('consumed')
                or (ticket.get('project_id'), ticket.get('job_id')) != (pid, jid)
                or not 0 <= _stamp_age(ticket.get('created_at')) <= TTL):
            raise core.WorkflowError('核驗已過期或已使用，請重新核驗')
        ticket['consumed'] = True
        core.write_json(token_path, ticket)
        op = {'id': secrets.token_hex(16), 'project_id': pid, 'job_id': jid, 'owner': owner,
              'request_id': request_id, 'created_at': core.now(), 'confirmed_at': core.now(),
              'fingerprint': ticket['fingerprint'], 'state': 'checking', 'executed': False,
              'message': '正在再次核驗設備與耗材，尚未發送'}
        core.write_json(_operation_path(op['id']), op)
    try:
        (launch or _launch)(op)
    except Exception:
        op.update(state='blocked', message='後台執行器未啟動，未發送；請重新核驗', updated_at=core.now())
        core.write_json(_operation_path(op['id']), op)
    return _public(op)

def _launch(op):
    threading.Thread(target=_run, args=(op,), daemon=True, name='printlab-workbench-send').start()

def _run(op):
    path = _operation_path(op['id'])
    pid, jid = op['project_id'], op['job_id']
    try:
        result = check(pid, jid)
        if not result['ready'] or result['fingerprint'] != op['fingerprint']:
            op.update(state='blocked', message='設備、材料、文件或發送能力已變化，請重新核驗；未發送', checks=result['checks'])
            return
        core.approve(pid, jid)
        op.update(state='dispatching', message='正在通過已綁定通道發送；尚未確認設備已開始')
        core.write_json(path, op)
        from . import studio_bridge
        try:
            if result['transport'].get('kind') == 'bambuddy_queue':
                from . import queue_sender
                result = queue_sender.dispatch(pid, jid)
            else:
                result = studio_bridge.dispatch(pid, jid)
        except studio_bridge.BeforeSendError:
            op.update(state='blocked', executed=False, message='發送準備未通過，已確認未發起發送；可重新核驗')
            return
        if result.get('command_sent') is not True:
            raise core.WorkflowError('發送執行器未證實已發起發送')
        op.update(state='submitted', executed=result.get('executed', False), message='發送操作已結束，等待設備讀回', result=result)
        observed = bambuddy.reconcile(pid, jid)
        op['observation'] = {k: observed.get(k) for k in ('matching_task', 'fresh', 'device_state')}
        if observed.get('matching_task') and observed.get('fresh'):
            op.update(state='observed', message='設備已讀回匹配任務；首層與實物仍需檢查')
        # Dispatch receipts alone never prove physical extrusion.
        if op['state'] != 'observed':
            op['message'] = '已發起發送，尚未匹配到設備任務；不會重複發送'
    except Exception:
        dispatched = op.get('state') in {'dispatching', 'submitted', 'observed'} or (core.job_path(pid, jid) / 'dispatch.json').exists()
        op.update(state='unknown' if dispatched else 'blocked', executed=False,
            message='發送結果需要核對，不會自動重發' if dispatched else '核驗或準備未通過，未發送；請查看任務記錄')
    finally:
        op['updated_at'] = core.now()
        core.write_json(path, op)
