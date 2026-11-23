"""Explicit shelf of prepared prints and GET-only readiness checks.

Registration is not print authorization. This module never approves, uploads,
reserves a queue slot, changes hardware, or starts a print. A caller must bind a
fresh user action and repeat readiness immediately before actual dispatch.
"""
from __future__ import annotations

import math
import re
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import quote

from . import core, bambuddy, design, native, slicer_guard, materials

REGISTRY = 'Library/Prepared/list.json'
PREPARED_STATES = {'awaiting_configuration', 'awaiting_approval', 'approved'}


def _registry():
    value = core.read_json(core.ROOT / REGISTRY, {'schema_version': 1, 'items': []})
    if not isinstance(value, dict) or value.get('schema_version') != 1 or not isinstance(value.get('items'), list):
        raise core.WorkflowError('待打印清單格式損壞，請先修復清單')
    return value


def _number(value):
    try:
        if isinstance(value, bool):
            return None
        v = float(value)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None


def slot_label(slot):
    if slot == 254:
        return '左主外掛'
    if slot == 255:
        return '右輔外掛'
    if type(slot) is int and 0 <= slot < 104:
        return f'{chr(65 + slot // 4)}{slot % 4 + 1}'
    return '槽位待核實'


def _url(pid, relative):
    return f'/api/files/{quote(pid, safe="")}/{quote(relative, safe="/")}'


def _slice_info(jd, job):
    """Use selected plate's used rows; global unused project IDs are not parts."""
    import json
    with zipfile.ZipFile(core.safe_path(jd, job['artifact'])) as z:
        root = ET.fromstring(z.read('Metadata/slice_info.config'))
        settings = json.loads(z.read('Metadata/project_settings.config'))
    plates = [p for p in root.findall('.//plate') if any(
        m.get('key') == 'index' and m.get('value') == str(job.get('plate', 1)) for m in p.findall('metadata'))]
    if len(plates) != 1:
        raise core.WorkflowError('切片缺少唯一板號')
    plate = plates[0]
    meta = {m.get('key'): m.get('value') for m in plate.findall('metadata')}
    rows = [dict(f.attrib) for f in plate.findall('.//filament')]
    ids = [int(row['id']) for row in rows]
    if not rows or len(set(ids)) != len(ids) or any(i < 1 for i in ids):
        raise core.WorkflowError('切片材料編號缺失或重複')
    for row in rows:
        row['id'] = int(row['id'])
        row['used_g'] = _number(row.get('used_g'))
        if row['used_g'] is None or row['used_g'] < 0:
            raise core.WorkflowError('切片缺少每種材料的用量，不能核驗剩料')
    total = _number(meta.get('weight'))
    if total is None or total <= 0 or abs(sum(r['used_g'] for r in rows) - total) > max(.1, total * .001):
        raise core.WorkflowError('分材料用量與本盤總用量不一致，需重新檢查切片')
    return settings, rows, meta


def _bindings(job, rows):
    mapping = job.get('mapping', {})
    slots = mapping.get('ams_mapping', [])
    ids = mapping.get('project_filament_ids', list(range(1, len(slots) + 1)))
    if (not slots or not isinstance(ids, list) or len(ids) != len(slots)
            or any(type(i) is not int or i < 1 for i in ids) or len(set(ids)) != len(ids)
            or any(type(s) is not int or s < 0 for s in slots)):
        raise core.WorkflowError('耗材料槽映射不完整')
    if set(ids) != {r['id'] for r in rows}:
        raise core.WorkflowError('任務材料編號與本盤實際使用編號不一致')
    by_id = {r['id']: r for r in rows}
    result = []
    for index, fid in enumerate(ids):
        row = by_id[fid]
        def mapped(key, fallback=None):
            values = mapping.get(key, [])
            return values[index] if isinstance(values, list) and index < len(values) else fallback
        result.append({'filament_id': fid, 'slot': slots[index], 'slot_label': slot_label(slots[index]),
            'required_grams': row['used_g'],
            'material': mapped('filament_types', row.get('type')),
            'series': mapped('filament_series', mapping.get('material') or row.get('type')),
            'color': mapped('filament_colours', mapping.get('color') or row.get('color')),
            'name': mapped('material_display_names', mapped('filament_series', row.get('type'))),
            'profile_id': row.get('tray_info_idx'), 'inventory_id': mapped('inventory_ids'),
            'support_only': row.get('used_for_object') == 'false' and row.get('used_for_support') == 'true'})
    return result


def _entry(pid, jid):
    pid = core.read_json(core.project_path(pid) / 'project.json')['id']
    matches = [r for r in _registry()['items'] if r.get('project_id') == pid and r.get('job_id') == jid and r.get('active', True)]
    if len(matches) != 1:
        raise core.WorkflowError('此任務尚未加入待打印清單，或已移出')
    return matches[0]


def register(pid, jid, *, title=None, parts=None, note=None):
    """Explicitly publish one checked local job to the shelf, never authorize it."""
    p, jd = core.project_path(pid), core.job_path(pid, jid)
    job = core.read_json(jd / 'job.json')
    pid = core.read_json(p / 'project.json')['id']
    if job.get('project_id') != pid or job.get('id') != jid:
        raise core.WorkflowError('任務身份不匹配')
    if job.get('state') not in PREPARED_STATES or (jd / 'dispatch.json').exists():
        raise core.WorkflowError('只能加入尚未發送的已切片任務；不得重複打印舊回執')
    if core.print_configuration_issues(job):
        raise core.WorkflowError('試切片或配置不完整的任務不能加入待打印清單')
    registration_issue = None
    if core.read_json(p / 'project.json').get('current_revision') != job.get('revision'):
        # A shelf is an inventory of intended work, not a release gate. Preserve
        # a previous component's immutable package visibly, without changing the
        # project revision or inventing a valid current dispatch fingerprint.
        core.validate_3mf(jd / job['artifact'], job.get('plate', 1))
        if core.revision_files(p, job['revision']) != job['source_hashes']:
            raise core.WorkflowError('舊版本源文件已變化，不能登記原打印包')
        for group in ('profile_hashes', 'input_hashes'):
            for rel, expected in job.get(group, {}).items():
                if group == 'input_hashes' and not rel.startswith('Input/'):
                    raise core.WorkflowError('受控切片輸入路徑不正確')
                if core.digest(core.safe_path(jd, rel)) != expected:
                    raise core.WorkflowError('舊打印包的配置或輸入已變化')
        if core.digest(core.safe_path(jd, job['artifact'])) != job.get('artifact_sha256'):
            raise core.WorkflowError('舊版本切片已變化，不能登記原打印包')
        fingerprint = None
        registration_issue = '項目已有新版本；已保留此配件的舊打印包，打印前須重新準備並核驗'
    else:
        fingerprint = core.job_fingerprint(p, jd, job)
    _settings, rows, _meta = _slice_info(jd, job)
    _bindings(job, rows)
    if title is not None and (not isinstance(title, str) or not 1 <= len(title.strip()) <= 160):
        raise core.WorkflowError('請輸入簡短的配件名稱')
    if parts is not None and (not isinstance(parts, list) or len(parts) > 50 or any(not isinstance(x, str) or not x.strip() or len(x) > 160 for x in parts)):
        raise core.WorkflowError('配件列表格式不正確')
    if note is not None and (not isinstance(note, str) or len(note) > 1000):
        raise core.WorkflowError('備註過長')
    with core.lock('prepared-catalogue'):
        core.project_path(pid)
        data = _registry()
        prior = next((r for r in data['items'] if r.get('project_id') == pid and r.get('job_id') == jid), {})
        entry = {'project_id': pid, 'job_id': jid, 'revision': job['revision'],
                 'title': (title or prior.get('title') or core.read_json(p / 'project.json')['name']).strip(),
                 'parts': parts if parts is not None else prior.get('parts', []),
                 'note': note if note is not None else prior.get('note', ''),
                 'fingerprint': fingerprint, 'artifact_sha256': job['artifact_sha256'],
                 'registration_issue': registration_issue,
                 'created_at': prior.get('created_at') or core.now(), 'updated_at': core.now(),
                 'active': True, 'automatic_start': False, 'print_authorized': False}
        data['items'] = [r for r in data['items'] if (r.get('project_id'), r.get('job_id')) != (pid, jid)] + [entry]
        data['updated_at'] = core.now()
        core.write_json(core.ROOT / REGISTRY, data)
    return card(entry)


def card(entry):
    """Cheap shelf card. Does not claim that live conditions are ready."""
    pid, jid = entry['project_id'], entry['job_id']
    base = {k: entry.get(k) for k in ('project_id', 'job_id', 'revision', 'title', 'parts', 'note', 'created_at', 'updated_at', 'registration_issue')}
    base.update(automatic_start=False, live_checked=False, state='prepared', state_label='待核驗', print_authorized=False)
    try:
        p, jd = core.project_path(pid), core.job_path(pid, jid)
        job = core.read_json(jd / 'job.json')
        if job.get('state') not in PREPARED_STATES or (jd / 'dispatch.json').exists():
            base.update(state=job.get('state', 'unavailable'), state_label='已發起或已歸檔')
        if core.read_json(p / 'project.json').get('current_revision') != job.get('revision'):
            base.update(state='stale', state_label='版本已更新，需重新核驗')
        settings, rows, meta = _slice_info(jd, job)
        base['materials'] = _bindings(job, rows)
        base['estimates'] = {'prediction_seconds': _number(meta.get('prediction')), 'weight_grams': _number(meta.get('weight')), 'kind': 'slicer_estimate'}
        base['bed_type'] = job.get('requested_bed_type')
        base['printer_id'] = job.get('printer_id')
        base['transport'] = job.get('mapping', {}).get('transport')
        revision = job['revision']
        for key, rel in [('preview_url', f'Preview/{revision}/cover.png'), ('model_url', f'Exports/{revision}/model.glb'),
                         ('artifact_url', f'Print/{jid}/{job["artifact"]}')]:
            try:
                core.safe_path(p, rel)
                base[key] = _url(pid, rel)
            except core.WorkflowError:
                base[key] = None
    except (core.WorkflowError, ValueError, KeyError, TypeError, OSError, ET.ParseError, zipfile.BadZipFile):
        base.update(state='unavailable', state_label='文件或材料記錄不可用', materials=[])
    return base


def catalogue():
    data = _registry()
    return {'items': [card(r) for r in data['items'] if r.get('active', True)],
            'updated_at': data.get('updated_at'), 'automatic_start': False}


def _spool_matches(spool, tray, bound):
    if not spool or spool.get('archived_at'):
        return False
    if (str(spool.get('rgba') or '').lstrip('#').upper() != str(tray.get('tray_color') or '').lstrip('#').upper()):
        return False
    family = str(spool.get('material') or '').upper()
    live = str(tray.get('tray_type') or '').upper()
    support = bound.get('profile_id') == 'GFS05' and tray.get('tray_info_idx') == 'GFS05'
    if family != live and not (support and family in {'SUPPORT FOR PLA', 'SUPPORT FOR PLA/PETG'} and live in {'PLA', 'PLA-S'}):
        return False
    subtype = str(spool.get('subtype') or '')
    if subtype and not support and subtype.lower() not in str(tray.get('tray_sub_brands') or '').lower():
        return False
    return True


def quantity_checks(bindings, status, assignments, spools):
    """Aggregate by physical slot, then use fresh RFID % × matched label weight.

    Historical/ledger remaining grams are deliberately never used. A matched
    assignment plus exact expected material/color is needed to lend label weight
    to the currently loaded spool. This is a conservative estimate, not a scale.
    """
    trays = bambuddy.reported_trays(status)
    assigned = {}
    for a in assignments:
        if a.get('printer_id') != status.get('id'):
            continue
        key = (a.get('ams_id'), a.get('tray_id'))
        if key in assigned:
            assigned[key] = None  # Ambiguous current assignment must fail closed.
        else:
            assigned[key] = a.get('spool_id')
    spool_rows = {}
    for spool in spools:
        sid = spool.get('id')
        spool_rows[sid] = None if sid in spool_rows else spool
    grouped = {}
    for bound in bindings:
        slot = bound['slot']
        item = grouped.setdefault(slot, {**bound, 'filament_ids': [], 'required_grams': 0.0})
        item['required_grams'] += bound['required_grams']
        item['filament_ids'].append(bound['filament_id'])
        if any(item.get(k) != bound.get(k) for k in ('material', 'series', 'color', 'inventory_id', 'profile_id')):
            item['binding_conflict'] = True
    seen_spools = {}
    result = []
    for slot, item in grouped.items():
        tray = trays.get(slot, {})
        percent = _number(tray.get('remain'))
        if percent is None or not 0 <= percent <= 100 or materials.slot_state(tray) != 'loaded':
            percent = None
        sid = assigned.get((slot // 4, slot % 4)) if slot < 254 else None
        spool = spool_rows.get(sid)
        match = (sid is not None and (item.get('inventory_id') is None or sid == item['inventory_id'])
                 and _spool_matches(spool, tray, item) and not item.get('binding_conflict'))
        label_weight = _number(spool.get('label_weight')) if spool and match else None
        if label_weight is None or label_weight <= 0:
            label_weight = None
        estimate = percent * label_weight / 100 if percent is not None and label_weight else None
        reserve = max(10.0, item['required_grams'] * .1)
        sufficient = estimate is not None and estimate >= item['required_grams'] + reserve
        row = {k: item.get(k) for k in ('slot', 'slot_label', 'filament_ids', 'material', 'series', 'color', 'name')}
        row.update(required_grams=round(item['required_grams'], 2), reserve_grams=round(reserve, 2),
                   reported_remaining_percent=percent, label_weight_grams=label_weight,
                   estimated_available_grams=round(estimate, 2) if estimate is not None else None,
                   sufficient=sufficient, quantity_basis='device_percent_times_matched_spool_label' if estimate is not None else 'unknown',
                   message='按設備餘量估計足夠，已留餘量' if sufficient else '剩料不足' if estimate is not None else '餘量或當前料卷身份未知，不能確認足夠',
                   measured=False, inventory_id=sid if match else None)
        if sid is not None and match:
            if sid in seen_spools:
                row.update(sufficient=False, message='同一料卷被分配到多個物理槽位，需核對庫存綁定')
                seen_spools[sid].update(sufficient=False, message=row['message'])
            seen_spools[sid] = row
        result.append(row)
    return result


def check(pid, jid, *, client=None, inspector=None):
    """Read-only, approval-free preflight; no optimistic or cached readiness."""
    entry = _entry(pid, jid)
    p, jd = core.project_path(pid), core.job_path(pid, jid)
    job = core.read_json(jd / 'job.json')
    checks, quantities = [], []
    fingerprint, status, inspection, bindings, settings = None, None, None, [], None
    def record(key, label, passed, good, bad):
        checks.append({'id': key, 'label': label, 'status': 'pass' if passed else 'blocked', 'message': good if passed else bad})
    def probe(key, label, fn, good, bad):
        try:
            value = fn()
            record(key, label, True, good, bad)
            return value
        except (Exception,):
            record(key, label, False, good, bad)
            return None
    def integrity():
        if job.get('project_id') != entry['project_id'] or job.get('id') != jid or job.get('state') not in PREPARED_STATES or (jd / 'dispatch.json').exists():
            raise core.WorkflowError('不可重複發送')
        if core.print_configuration_issues(job):
            raise core.WorkflowError('配置未完成')
        fp = core.job_fingerprint(p, jd, job)
        if fp != entry['fingerprint'] or job.get('artifact_sha256') != entry['artifact_sha256']:
            raise core.WorkflowError('已登記打印包發生變化')
        return fp
    fingerprint = probe('files', '版本與打印文件', integrity, '版本、切片、配置和登記指紋一致', '文件、版本、配置已變化或此任務已嘗試發送，請重新準備')
    def design_check():
        result = design.check(entry['project_id'], 'release', job['revision'])
        if result.get('status') not in {'passed', 'not_configured'}:
            raise core.WorkflowError('設計放行未通過')
        return True
    probe('design', '設計與模型檢查', design_check, '模型已通過項目的放行檢查', '當前模型的放行記錄缺失或不匹配')
    def file_checks():
        nonlocal settings, bindings
        # An outdated project revision still has useful immutable slice and
        # material facts. Inspect those independently of the release gate above;
        # never let that independence turn a failed fingerprint into readiness.
        artifact = core.safe_path(jd, job['artifact'])
        if core.digest(artifact) != job.get('artifact_sha256') or job.get('artifact_sha256') != entry.get('artifact_sha256'):
            raise core.WorkflowError('已登記切片發生變化')
        settings, rows, _meta = _slice_info(jd, job)
        bindings = _bindings(job, rows)
        slicer_guard.assert_safe_archive(artifact, job.get('plate', 1))
        value = (inspector or native.run_client)(jd, job, 'inspect')
        if not value or value.get('ok') is not True or value.get('executed') is not False:
            raise core.WorkflowError('獨立刀路檢查失敗')
        return value
    inspection = probe('gcode', '刀路與啟動指令', file_checks, '刀路、載料和溫度指令檢查通過', '刀路、啟動指令或用料數據未通過檢查')
    if job.get('printer_provider') == 'official_studio':
        binding = core.studio_device_binding()
        record('identity', '本機 Studio 印表機身份', bool(binding and job.get('studio_device_binding') == binding),
               '任務綁定的 Studio 名稱、機型與序號一致', '本機 Studio 印表機身份缺失或已變更')
        facts = {}
        plate = core.read_json(core.DEVICE_CARD, {}).get('user_confirmed', {}).get('build_plate_description')
        record('plate_type', '打印板類型', plate == job.get('requested_bed_type') == job.get('curr_bed_type'),
               '切片與已確認的打印板類型一致', '切片板型與已確認的打印板類型不符')
        probe('active_receipts', '歷史發送結果', lambda: (bambuddy.ensure_no_active_dispatches(jd), True)[1],
              '沒有其他活動或結果不明的發送記錄', '有其他正在執行或結果不明的記錄，需先對帳')
        blockers = [c for c in checks if c['status'] == 'blocked']
        return {'project_id':entry['project_id'],'job_id':jid,'fingerprint':fingerprint,'checked_at':core.now(),
                'ready':not blockers,'checks':checks,'blockers':blockers,'materials':quantities,
                'transport':{'kind':'bambu_studio_manual','manual':True,'independent_dispatch_verified':False,
                             'message':'Windows 使用者在官方 Studio 手動核對與發送；此預檢不控制印表機。'},
                'device':{'name':(binding or {}).get('studio_printer_name'),
                          'model':(binding or {}).get('studio_printer_model'),'state':'user_verified_at_task'},
                'device_facts':facts,'plate_confirmation_required':False,'executed':False,'automatic_start':False,
                'quantity_note':'Spoolman 餘量是台帳估算；實際裝料狀態仍未知。'}
    own_client = client is None
    try:
        client = client or bambuddy.Client()
        def read_status():
            value = client.get(f"printers/{job['printer_id']}/status")
            if not isinstance(value, dict):
                raise core.WorkflowError('設備返回格式不正確')
            return value
        status = probe('connection', '實時設備連接', read_status, '已讀取設備實時狀態', '無法讀取打印機實時狀態')
        if isinstance(status, dict):
            age = bambuddy.telemetry_age(status)
            fresh = status.get('connected') is True and age is not None and -5 <= age <= 30
            record('freshness', '狀態新鮮度', fresh, '設備已連接，AMS報告在30秒內', '設備離線，或狀態超過30秒/時間未知')
            record('identity', '目標設備', status.get('id') == job.get('printer_id'), '設備編號與打印包一致', '設備編號不匹配，不能打印')
            record('idle', '設備空閒', status.get('state') in {'IDLE', 'FINISH'}, '設備空閒或已結束上一盤', '設備正在工作、暫停或故障中，請等待或處理')
            record('diagnostics', '設備故障', not status.get('hms_errors'), '沒有活動故障報告', '設備有活動故障，請先處理')
            temps = status.get('temperatures')
            quiet = (isinstance(temps, dict) and all(k in temps for k in ('bed_target', 'nozzle_target'))
                     and all(_number(v) == 0 for k, v in temps.items() if k.endswith('_target')))
            record('heaters', '加熱與其他作業', quiet, '沒有正在執行的加熱目標', '設備正在加熱，或加熱狀態未知')
            if bindings and fresh:
                def check_slots():
                    bambuddy.verify_machine_identity(client, job)
                    bambuddy.validate_ready(status, job['mapping'], cleared_finished=True)
                    return True
                probe('slots', '設備料槽', check_slots, '設備連線與料槽資料可讀', '料槽資料不可讀或設備狀態不允許發送')
                expected = (inspection or {}).get('inspection', {}).get('nozzleDiameters')
                actual = [_number(n.get('nozzle_diameter')) for n in status.get('nozzles', [])]
                nozzle_ok = (isinstance(expected, list) and len(expected) == len(actual) and bool(actual)
                             and all(_number(a) == _number(b) and _number(a) is not None for a, b in zip(expected, actual)))
                expected_types = (inspection or {}).get('inspection', {}).get('nozzleTypes')
                actual_types = [{'HS01': 'hardened_steel', 'SS01': 'stainless_steel'}.get(n.get('nozzle_type')) for n in status.get('nozzles', [])]
                nozzle_ok = nozzle_ok and expected_types == actual_types and all(actual_types)
                record('nozzles', '噴嘴規格', nozzle_ok, '實際噴嘴直徑和類型與切片一致', '實際噴嘴規格未知或不符')
                def quantity():
                    assignments, spools = client.get('inventory/assignments'), client.get('inventory/spools')
                    if not isinstance(assignments, list) or not isinstance(spools, list):
                        raise core.WorkflowError('庫存返回格式不正確')
                    return quantity_checks(bindings, status, assignments, spools)
                try:
                    quantities = quantity()
                except Exception:
                    quantities = []
            else:
                record('slots', '設備料槽', False, '', '文件或實時數據未通過，無法核驗料槽')
                record('quantity', '耗材餘量', False, '', '實時數據不足，無法核驗餘量')
            physical_plate = core.read_json(core.DEVICE_CARD, {}).get('user_confirmed', {}).get('build_plate_description')
            record('plate_type', '打印板類型', physical_plate == job.get('requested_bed_type') == job.get('curr_bed_type'), '切片與已確認的打印板類型一致，仍需確認板面乾淨', '切片板型與當前設備卡不一致或未確認')
        def queue_check():
            rows = client.get('queue/')
            if not isinstance(rows, list) or any(r.get('status') in {'pending', 'printing'} for r in rows):
                raise core.WorkflowError('隊列佔用或狀態未知')
            return True
        probe('queue', '其他排隊任務', queue_check, '沒有其他待打或打印隊列', '另有排隊/打印任務，或隊列狀態讀取失敗')
    except Exception:
        record('device', '設備讀取', False, '', '設備接口不可用，未發起任何打印')
    finally:
        if own_client and client:
            client.close()
    probe('active_receipts', '歷史發送結果', lambda: (bambuddy.ensure_no_active_dispatches(jd), True)[1], '沒有其他活動或結果不明的發送記錄', '有其他正在執行或結果不明的記錄，需先對帳，不能重複發送')
    blockers = [c for c in checks if c['status'] == 'blocked']
    transport = job.get('mapping', {}).get('transport')
    return {'project_id': entry['project_id'], 'job_id': jid, 'fingerprint': fingerprint, 'checked_at': core.now(),
            'ready': not blockers, 'checks': checks, 'blockers': blockers, 'materials': quantities,
            'transport': {'kind': transport, 'developer_mode': (status or {}).get('developer_mode'),
                          'sdcard': (status or {}).get('sdcard'),
                          'independent_dispatch_verified': False,
                          'message': '需由發送適配器另行核驗可用性；此結果不代表已能獨立發送'},
            'device': {k: (status or {}).get(k) for k in ('id', 'name', 'state', 'current_print')},
            'plate_confirmation_required': False, 'executed': False, 'automatic_start': False,
            'quantity_note': '餘量按設備百分比和當前綁定料卷的標稱克重估計，可能滯後；不是實稱值。'}
