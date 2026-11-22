"""Register user-confirmed spools with durable request reconciliation."""
from __future__ import annotations

import hashlib
import json
import re

import httpx

from . import bambuddy, core, materials, supplies, workspace


JOURNAL = 'Library/Materials/intake.json'
FIELDS = {'material', 'brand', 'subtype', 'color_name', 'rgba', 'material_number',
          'storage_location', 'label_weight', 'core_weight'}


def _payload(spool, source):
    if not isinstance(spool, dict) or set(spool) - FIELDS:
        raise core.WorkflowError('Unsupported spool fields; use material, product, colour and storage facts')
    result = {'material': workspace.required_text(spool.get('material'), 'Material', 50)}
    for key, value in spool.items():
        if key in {'label_weight', 'core_weight'}:
            if type(value) is not int or value < 0:
                raise core.WorkflowError(f'{key} must be a nonnegative integer in grams')
            result[key] = value
        elif key == 'rgba':
            if not isinstance(value, str) or not re.fullmatch(r'[0-9a-fA-F]{8}', value):
                raise core.WorkflowError('rgba must contain eight hexadecimal digits')
            result[key] = value.upper()
        else:
            result[key] = workspace.required_text(value, key, 255)
    # Upstream defaults to a full 1000g spool. Explicit zero leaves unknown weight unknown.
    result.setdefault('label_weight', 0)
    result.setdefault('core_weight', 0)
    result.update(weight_used=0, data_origin='manual', note=f'用戶確認的庫存記錄\n來源 {source}\n實際餘量未知。')
    return result


def register(spool, source, request_id, client_factory=None, *, preview=False):
    """One request describes one physical spool. Reuse it after interruption."""
    source = workspace.required_text(source, 'User confirmation source')
    request_id = workspace.required_text(request_id, 'Request ID', 100)
    if core.config().get('spoolman_url'):
        return _register_spoolman(spool, source, request_id, preview=preview)
    if preview:
        raise core.WorkflowError('Intake preview requires a configured Spoolman source')
    payload = _payload(spool, source)
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    with core.lock('material-intake'):
        path = core.safe_path(core.ROOT, JOURNAL, require_file=False)
        journal = core.read_json(path, {'schema_version': 1, 'requests': {}})
        existing = journal['requests'].get(request_id)
        service = workspace.connection()['bambuddy_url']
        if existing and (existing['fingerprint'] != fingerprint or existing['service'] != service):
            raise core.WorkflowError('This intake request already describes another spool or service')
        marker = (existing or {}).get('marker') or '[PrintLab intake ' + hashlib.sha256(
            f'{core.ROOT}:{request_id}'.encode()).hexdigest() + ']'
        payload['note'] += '\n' + marker
        client = (client_factory or bambuddy.Client)(write=True)
        try:
            rows = client.get('inventory/spools')
            if not isinstance(rows, list):
                raise core.WorkflowError('Unexpected inventory response')
            matches = [row for row in rows if marker in str(row.get('note') or '')]
            if len(matches) > 1:
                raise core.WorkflowError('Multiple spools carry the intake marker; reconcile their identities')
            if matches:
                row = matches[0]
                if any(row.get(key) != value for key, value in spool.items() if key != 'rgba'):
                    raise core.WorkflowError('The registered spool was changed; inspect it before continuing')
                if 'rgba' in spool and str(row.get('rgba')).upper() != payload['rgba']:
                    raise core.WorkflowError('The registered spool colour changed; inspect it before continuing')
                journal['requests'][request_id] = {'status': 'registered', 'spool_id': row['id'],
                    'fingerprint': fingerprint, 'service': service, 'marker': marker, 'observed_at': core.now()}
                core.write_json(path, journal)
                return {'request_id': request_id, 'replayed': True, 'spool': materials.inventory_items([row])[0]}
            if existing:
                raise core.WorkflowError('Previous intake result is unresolved or the spool was removed. '
                                         'Inspect Bambuddy and the saved request before another write; no retry was sent')
            journal['requests'][request_id] = {'status': 'pending', 'fingerprint': fingerprint,
                'service': service, 'marker': marker, 'started_at': core.now()}
            core.write_json(path, journal)
            row = client.post('inventory/spools', json=payload)
            if type(row.get('id')) is not int:
                raise core.WorkflowError('Intake response has no spool ID; rerun this same request to reconcile')
            observed = client.get(f"inventory/spools/{row['id']}")
            if observed.get('id') != row['id'] or marker not in str(observed.get('note') or ''):
                raise core.WorkflowError('Spool readback did not match; keep the request for reconciliation')
            journal['requests'][request_id].update(status='registered', spool_id=row['id'], observed_at=core.now())
            core.write_json(path, journal)
            return {'request_id': request_id, 'replayed': False, 'spool': materials.inventory_items([observed])[0]}
        finally:
            client.close()


_SPOOLMAN_FIELDS = {'spoolman_filament_id', 'remaining_weight', 'label_weight', 'core_weight', 'storage_location'}


def _spoolman_payload(spool, source, marker):
    if not isinstance(spool, dict) or set(spool) - _SPOOLMAN_FIELDS:
        raise core.WorkflowError('Spoolman intake accepts the confirmed filament ID, weights and storage location')
    fid = spool.get('spoolman_filament_id')
    if type(fid) is not int or fid <= 0:
        raise core.WorkflowError('Spoolman intake needs a positive spoolman_filament_id from the filament catalog')
    payload = {'filament_id': fid, 'comment': f'PrintLab 登記\n來源：{source}\n{marker}'}
    if len(payload['comment']) > 1024:
        raise core.WorkflowError('Use a shorter confirmation source; Spoolman limits spool comments to 1024 characters')
    for local, remote in [('label_weight', 'initial_weight'), ('core_weight', 'spool_weight'),
                          ('remaining_weight', 'remaining_weight')]:
        if local in spool:
            value = materials.number(spool[local])
            if value is None or value < 0 or (local == 'label_weight' and value == 0):
                raise core.WorkflowError(f'{local} must be a valid weight in grams')
            payload[remote] = value
    if 'storage_location' in spool:
        payload['location'] = workspace.required_text(spool['storage_location'], 'Storage location', 64)
    return payload


def _verify_spoolman_weight(payload, filament):
    # Spoolman assumes a full spool when it knows initial weight and receives no usage.
    initial = payload.get('initial_weight', filament.get('weight'))
    remaining = payload.get('remaining_weight')
    if remaining is None and materials.number(initial) is not None:
        raise core.WorkflowError('Provide confirmed remaining_weight in grams. Spoolman otherwise records this spool as full.')
    if remaining is not None and (materials.number(initial) is None or not 0 < initial or remaining > initial):
        raise core.WorkflowError('Confirmed remaining_weight requires a positive initial weight and cannot exceed it')


def _spoolman_json(client, method, path, **kwargs):
    try:
        response = client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        status = f' (HTTP {exc.response.status_code})' if isinstance(exc, httpx.HTTPStatusError) else ''
        raise core.WorkflowError(f'Spoolman could not complete {method}{status}. Reuse the same request ID after a write error.') from exc


def _spoolman_match(row, payload, marker):
    if not isinstance(row, dict) or type(row.get('id')) is not int:
        return False
    filament = row.get('filament')
    return (isinstance(filament, dict) and filament.get('id') == payload['filament_id']
            and marker in str(row.get('comment') or '').splitlines())


def _register_spoolman(spool, source, request_id, *, preview):
    service = supplies.sources().get('spoolman_url')
    if not service:
        raise core.WorkflowError('The configured Spoolman URL must be a service root without credentials or a query')
    marker = '[PrintLab intake ' + hashlib.sha256(f'{core.ROOT}:{request_id}'.encode()).hexdigest() + ']'
    payload = _spoolman_payload(spool, source, marker)
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    identity = {'provider': 'spoolman', 'service': service, 'fingerprint': fingerprint, 'marker': marker}
    with core.lock('material-intake'), supplies.http_client(base_url=service + '/api/v1/') as client:
        journal_path = core.safe_path(core.ROOT, JOURNAL, require_file=False)
        journal = core.read_json(journal_path, {'schema_version': 1, 'requests': {}})
        requests = journal['requests']
        existing = requests.get(request_id)
        if existing and any(existing.get(k) != v for k, v in identity.items()):
            raise core.WorkflowError('This intake request already describes another spool or service')
        if existing:
            if type(existing.get('spool_id')) is int:
                candidates = [_spoolman_json(client, 'GET', f"spool/{existing['spool_id']}")]
            else:
                candidates = _spoolman_json(client, 'GET', 'spool', params={'allow_archived': 'true'})
                if not isinstance(candidates, list) or any(not isinstance(row, dict) for row in candidates):
                    raise core.WorkflowError('Unexpected Spoolman inventory response; prior registration remains unresolved')
            matches = [row for row in candidates if marker in str(row.get('comment') or '').splitlines()]
            if len(matches) != 1 or not _spoolman_match(matches[0], payload, marker):
                raise core.WorkflowError('Previous Spoolman result is unresolved or changed; inspect it before another write')
            observed = matches[0]
            replayed = True
        else:
            filament = _spoolman_json(client, 'GET', f"filament/{payload['filament_id']}")
            if not isinstance(filament, dict) or filament.get('id') != payload['filament_id']:
                raise core.WorkflowError('Spoolman did not return the requested filament')
            _verify_spoolman_weight(payload, filament)
            if preview:
                vendor = filament.get('vendor') or {}
                return {'state': 'preview', 'provider': 'spoolman', 'request_id': request_id,
                        'filament': {k: filament.get(k) for k in ('id', 'name', 'material', 'color_hex')},
                        'brand': vendor.get('name') if isinstance(vendor, dict) else None,
                        'remaining_weight': payload.get('remaining_weight')}
            requests[request_id] = {**identity, 'status': 'pending', 'started_at': core.now()}
            core.write_json(journal_path, journal)
            created = _spoolman_json(client, 'POST', 'spool', json=payload)
            sid = created.get('id') if isinstance(created, dict) else None
            if type(sid) is not int:
                raise core.WorkflowError('Spoolman intake response has no spool ID; reuse the same request ID')
            requests[request_id]['spool_id'] = sid
            core.write_json(journal_path, journal)
            observed = _spoolman_json(client, 'GET', f'spool/{sid}')
            if not _spoolman_match(observed, payload, marker):
                raise core.WorkflowError('Spoolman readback did not match; keep the request for reconciliation')
            replayed = False
        if not preview:
            requests[request_id].update(status='registered', spool_id=observed['id'], observed_at=core.now())
            core.write_json(journal_path, journal)
        return {'state': 'registered', 'provider': 'spoolman', 'request_id': request_id, 'replayed': replayed,
                'spool': {'id': observed['id'], 'filament_id': payload['filament_id'],
                          'remaining_weight': observed.get('remaining_weight'), 'archived': observed.get('archived', False)}}
