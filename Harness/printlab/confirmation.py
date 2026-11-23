"""Exact-task confirmation facts and a read-only card; no device writes."""
from __future__ import annotations

import datetime as dt
import re
import uuid
from . import core

FACTS = {'print_authorized', 'plate_clear', 'material_loaded', 'device_ready',
         'design_selected', 'colors_selected'}


def _age(stamp):
    try:
        parsed = dt.datetime.fromisoformat(stamp)
        if parsed.tzinfo is None:
            return None
        return (dt.datetime.now(dt.timezone.utc) - parsed).total_seconds()
    except (TypeError, ValueError):
        return None


def record(pid, jid, facts, quote, source, confirmed_at=None):
    if not isinstance(facts, dict) or not facts or set(facts) - FACTS or any(type(v) is not bool for v in facts.values()):
        raise core.WorkflowError('Confirmation facts must be explicit supported boolean fields')
    if not isinstance(quote, str) or not quote.strip() or not isinstance(source, str) or not source.strip():
        raise core.WorkflowError('Record the actual user quote and conversation source')
    if confirmed_at is not None:
        age=_age(confirmed_at)
        if age is None or age < 0:
            raise core.WorkflowError('Confirmation time must be a timezone-aware past user-message timestamp')
    with core.lock('printer'):
        p, jd = core.project_path(pid), core.job_path(pid, jid)
        job = core.read_json(jd / 'job.json')
        if (jd / 'dispatch.json').exists() or job.get('state') not in {'awaiting_approval', 'awaiting_configuration', 'approved'}:
            raise core.WorkflowError('Only a prepared, undispatched task can receive new confirmation facts')
        fingerprint = core.job_fingerprint(p, jd, job)
        event = {'id':'C'+uuid.uuid4().hex, 'job_id':jid, 'project_id':job['project_id'],
                 'recorded_at':core.now(), 'facts':facts, 'quote':quote.strip(), 'source':source.strip(),
                 'fingerprint':fingerprint, 'printer_id':job['printer_id']}
        if confirmed_at is not None:
            event['confirmed_at']=confirmed_at
        core.write_json(jd / 'Confirmations' / (event['id']+'.json'), event)
        return event


def events(jd, job, fingerprint):
    rows = []
    for path in (jd / 'Confirmations').glob('C*.json'):
        if path.is_symlink():
            continue
        row = core.read_json(path, {})
        if row.get('job_id') == job['id'] and row.get('fingerprint') == fingerprint and row.get('printer_id') == job.get('printer_id'):
            rows.append(row)
    return sorted(rows, key=lambda r:r.get('recorded_at', ''))


def resolve(jd, job, fingerprint, event_id=None):
    if event_id is not None and not re.fullmatch(r'C[0-9a-f]{32}', event_id):
        raise core.WorkflowError('Invalid confirmation event ID')
    rows = events(jd, job, fingerprint)
    if event_id is not None:
        if not any(row.get('id') == event_id for row in rows):
            raise core.WorkflowError('Confirmation does not match this exact task')
        # Later corrections or withdrawals override an older selected event.
    facts = {}
    for row in rows:
        for name,value in row.get('facts', {}).items():
            if name in FACTS:
                facts[name] = {'value':value,'quote':row.get('quote'),'source':row.get('source'),
                               'recorded_at':row.get('confirmed_at') or row.get('recorded_at'),'event_id':row.get('id')}
    for name in ('plate_clear','print_authorized','material_loaded','device_ready'):
        fact = facts.get(name)
        if fact:
            age = _age(fact['recorded_at'])
            fact['fresh'] = age is not None and 0 <= age <= 1800
    return facts


def approval_facts(pid, jid, event_id):
    p, jd = core.project_path(pid), core.job_path(pid, jid)
    job = core.read_json(jd/'job.json')
    fingerprint = core.job_fingerprint(p,jd,job)
    facts = resolve(jd,job,fingerprint,event_id)
    return facts


def card(pid, jid=None, device=None):
    p = core.project_path(pid)
    project = core.read_json(p/'project.json')
    if not jid:
        jid = (core.current_attempt(p, project) or {}).get('id')
    plate = core.read_json(core.DEVICE_CARD,{}).get('user_confirmed',{}).get('build_plate_description')
    if not jid:
        return {'project_id':project['id'],'project_name':project['name'],'revision':project.get('current_revision'),
                'job_id':None,'plate_type':plate,'missing':[{'key':'slice','label':'尚未準備具體切片任務','needs_user':False}],
                'can_approve':False,'already_dispatched':False,'facts':{}}
    jd = core.job_path(pid,jid)
    job = core.read_json(jd/'job.json')
    dispatched = (jd/'dispatch.json').exists()
    issues = core.print_configuration_issues(job)
    fingerprint = None
    try:
        fingerprint = core.job_fingerprint(p,jd,job)
    except (core.WorkflowError,OSError) as exc:
        issues.append(str(exc))
    facts = resolve(jd,job,fingerprint) if fingerprint else {}
    missing=[{'key':'configuration','label':issue,'needs_user':False} for issue in issues]
    if device is None:
        from . import supplies
        device=supplies.device()
    material_slots=[]
    mapping=job.get('mapping',{})
    raw=(device or {}).get('printer') or {}
    trays={u.get('id',0)*4+t.get('id',0):t for u in raw.get('ams',[]) for t in u.get('tray',[])}
    normalized_slots={s.get('diagnostics',{}).get('ams_id',0)*4+s.get('diagnostics',{}).get('tray_id',s.get('slot_number',1)-1):s
                      for module in (device or {}).get('material_slots',{}).get('modules',[]) for s in module.get('slots',[])}
    for i,slot in enumerate(mapping.get('ams_mapping',[])):
        t=trays.get(slot,{})
        normalized=normalized_slots.get(slot,{})
        material_slots.append({'filament_index':i+1,'slot_number':slot%4+1,'ams_id':slot//4,
                       'material':t.get('tray_sub_brands') or mapping.get('material'),'material_type':t.get('tray_type'),
                       'color':t.get('tray_color') or mapping.get('color'),
                       'english_label':normalized.get('english_label'), 'material_number':normalized.get('material_number'),
                       'slot_state':normalized.get('state')})
    fresh_device=(device or {}).get('state')=='online' and (device or {}).get('stale') is False
    return {'project_id':project['id'],'project_name':project['name'],'revision':job['revision'],'job_id':jid,
            'state':job['state'],'plate_type':job.get('curr_bed_type') or plate,'known_plate_type':plate,
            'artifact_sha256':job.get('artifact_sha256'),'estimates':job.get('estimates'),
            'material_slots':material_slots,'facts':facts,'missing':missing,'already_dispatched':dispatched,
            'can_approve':not missing and not dispatched and job.get('state') in {'awaiting_configuration','awaiting_approval','approved'},
            'device_fresh':fresh_device,'observed_at':(device or {}).get('updated_at'),
            'studio_device_binding':job.get('studio_device_binding'),
            'device_note':'未確認的設備就緒、材料與清板事實保持未知；依實際設備狀態檢查發送條件。'}
