"""Read inventory from Spoolman and planning snapshots from OpenSpoolMan."""
from __future__ import annotations

from html.parser import HTMLParser
import json
import re
import ssl
from urllib.parse import parse_qs, urlsplit

import httpx

from . import bambuddy, core, materials


_SOURCES = ('spoolman_url', 'openspoolman_url')
_VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
_ERRORS = (httpx.HTTPError, ValueError, TypeError, OSError, core.WorkflowError)


def sources():
    result = {}
    cfg = core.config()
    for key in _SOURCES:
        value = cfg.get(key)
        if not isinstance(value, str):
            continue
        try:
            url = urlsplit(value)
            if (url.scheme in {'http', 'https'} and url.hostname and url.username is None
                    and not url.query and not url.fragment and url.path in {'', '/'}):
                result[key] = value.rstrip('/')
        except ValueError:
            pass
    return result


def http_client(**options):
    # Use OS trust roots (including local CA installations on Windows).
    return httpx.Client(verify=ssl.create_default_context(), trust_env=False,
                        follow_redirects=False, timeout=6, **options)


def _get(url):
    with http_client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response


def _spoolman_rows(base):
    rows = _get(base + '/api/v1/spool').json()
    if not isinstance(rows, list) or any(not isinstance(r, dict) or type(r.get('id')) is not int
                                        or not isinstance(r.get('filament'), dict) for r in rows):
        raise ValueError('Invalid Spoolman inventory')
    return [row for row in rows if not row.get('archived')]


def _ledger_row(row):
    f = row['filament']
    vendor = f.get('vendor') or {}
    return {'id': row['id'], 'name': f.get('name'), 'material': f.get('material'),
            'brand': vendor.get('name') if isinstance(vendor, dict) else None,
            'color_name': f.get('name'), 'rgba': f.get('color_hex'),
            'label_weight': row.get('initial_weight') if row.get('initial_weight') is not None else f.get('weight'),
            'core_weight': row.get('spool_weight') if row.get('spool_weight') is not None else f.get('spool_weight'),
            'material_number': f.get('article_number'), 'weight_used': row.get('used_weight'),
            'storage_location': row.get('location'), 'data_origin': 'Spoolman'}


def inventory():
    if not core.config().get('spoolman_url'):
        return bambuddy.inventory()
    result = {'source': 'spoolman', 'state': 'unavailable', 'items': [], 'updated_at': None}
    base = sources().get('spoolman_url')
    if not base:
        return result
    try:
        rows = _spoolman_rows(base)
        items = materials.inventory_items([_ledger_row(row) for row in rows])
        for row, item in zip(rows, items):
            item['spoolman_filament_id'] = row['filament'].get('id')
            weight = materials.number(row.get('remaining_weight'))
            if weight is None or weight < 0:
                item.update(remaining_weight=None, estimated_remaining_weight=None, remaining_percent=None,
                            estimated_remaining_percent=None, quantity_basis='unknown')
            else:
                initial = materials.number(item.get('label_weight'))
                percent = round(weight / initial * 100, 2) if initial and 0 <= weight <= initial else None
                item.update(remaining_weight=weight, estimated_remaining_weight=weight, remaining_percent=percent,
                            estimated_remaining_percent=percent, quantity_basis='inventory_estimate')
        result.update(state='online', kind='inventory_ledger', items=items, updated_at=core.now(),
                      quantity_note='Spoolman 台帳估算；實際餘量未知，100% 不代表滿卷。')
    except _ERRORS as exc:
        result.update(error=type(exc).__name__, message='Spoolman 庫存目前無法讀取；未改用其他服務資料。')
    return result


class _OpenSpoolPage(HTMLParser):
    """Extract slot cards only; never follow Fill links or run page scripts."""

    def __init__(self):
        super().__init__()
        self.stack = []
        self.title = []
        self.cards = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get('class') or '').split())
        ams = self.stack[-1][1] if self.stack else None
        card = self.stack[-1][2] if self.stack else None
        capture = self.stack[-1][3] if self.stack else None
        if 'ams-card' in classes:
            ams = []
        if 'tray-card' in classes:
            card = {'module': ams, 'label': [], 'ledger': [], 'keys': []}
            self.cards.append(card)
        if tag == 'h5':
            if ams is not None and card is None:
                capture = ams
            elif any(frame[0] == 'header' for frame in self.stack):
                capture = self.title
        if card is not None:
            if 'card-header' in classes:
                capture = card['label']
            if 'tray-empty' in classes:
                card['empty'] = True
            if {'text-muted', 'mb-2'} <= classes:
                capture = card['ledger']
            if 'tray-color-swatch' in classes:
                match = re.search(r'background-color\s*:\s*#([A-Fa-f0-9]{8}|[A-Fa-f0-9]{6})\b', attrs.get('style') or '')
                if match:
                    card['rgba'] = match[1].upper()
            if tag == 'a' and (attrs.get('href') or '').startswith('/fill?'):
                q = parse_qs(urlsplit(attrs['href']).query)
                if all(len(q.get(k, [])) == 1 and re.fullmatch(r'\d{1,3}', q[k][0]) for k in ('ams', 'tray')):
                    card['keys'].append(tuple(int(q[k][0]) for k in ('ams', 'tray')))
        if tag not in _VOID:
            self.stack.append((tag, ams, card, capture))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1][3] is not None and data.strip():
            self.stack[-1][3].append(' '.join(data.split()))


def _active_tray(row):
    extra = row.get('extra') or {}
    value = extra.get('active_tray') if isinstance(extra, dict) else None
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            pass
    return value if isinstance(value, str) else None


def _slots(page, rows):
    by_id = {row['id']: row for row in rows}
    modules = {}
    seen = set()
    for card in page.cards:
        if len(card['keys']) != 1:
            raise ValueError('Unrecognized OpenSpoolMan tray card')
        aid, tid = card['keys'][0]
        if (aid, tid) in seen:
            raise ValueError('Duplicate OpenSpoolMan tray card')
        seen.add((aid, tid))
        external = (aid, tid) == (255, 254)
        name = '外掛料卷' if external else ' '.join(card['module'] or [])
        if not name:
            raise ValueError('OpenSpoolMan AMS name is missing')
        module = modules.setdefault(aid, {'name': name, 'is_external': external, 'slots': []})
        label = ' '.join(card['label'])
        match = re.search(r'(?:Tray\s+\d+|External Spool)\s*-\s*([\w.+-]+)', label)
        material = match[1] if match and not card.get('empty') else None
        match = re.match(r'#(\d+)\b', ' '.join(card['ledger']))
        spool_id = int(match[1]) if match and not card.get('empty') else None
        row = by_id.get(spool_id)
        entry = _ledger_row(row) if row else {}
        tag = _active_tray(row) if row else None
        # A full private tray identifier includes the printer. Never join by AMS/tray suffix alone.
        conflicts = sorted(r['id'] for r in rows if r['id'] != spool_id and _active_tray(r) == tag
                           ) if tag and tag.endswith(f'_{aid}_{tid}') else []
        state = 'empty' if card.get('empty') else 'loaded' if material else 'unidentified' if spool_id else 'unknown'
        item = {'material': material, 'brand': entry.get('brand'), 'color_name': entry.get('color_name'),
                'rgba': card.get('rgba')}
        module['slots'].append({**item, 'slot_number': 1 if external else tid + 1, 'state': state,
            'english_label': materials.english_label(item) if state in {'loaded', 'unidentified'} else None,
            'spool_id': spool_id, 'ledger_conflict_ids': conflicts, 'fresh': False,
            'reported_remaining_percent': None, 'remaining_basis': 'unknown',
            'diagnostics': {'ams_id': aid, 'tray_id': tid}})
    if not modules:
        raise ValueError('OpenSpoolMan page contains no recognizable tray slots')
    for module in modules.values():
        module['slots'].sort(key=lambda slot: slot['slot_number'])
    result = list(modules.values())
    references = {}
    for module in result:
        for slot in module['slots']:
            if slot.get('spool_id') is not None:
                references[slot['spool_id']] = references.get(slot['spool_id'], 0) + 1
    for module in result:
        for slot in module['slots']:
            spool_id = slot.get('spool_id')
            if spool_id is not None and references[spool_id] > 1:
                slot['ledger_conflict_ids'] = sorted(set(slot['ledger_conflict_ids'] + [spool_id]))
    return result


def device():
    if not core.config().get('openspoolman_url'):
        return bambuddy.device()
    urls = sources()
    result = {'source': 'openspoolman', 'state': 'unavailable', 'printer': None, 'updated_at': None, 'stale': True,
              'message': '無法讀取 OpenSpoolMan 槽位頁；設備狀態未知。'}
    base = urls.get('openspoolman_url')
    if not base:
        return result
    try:
        response = _get(base + '/')
        page = _OpenSpoolPage()
        page.feed(response.text)
        page.close()
        rows = []
        if spoolman := urls.get('spoolman_url'):
            try:
                rows = _spoolman_rows(spoolman)
            except _ERRORS:
                pass  # The slot page is still useful without the inventory service.
        modules = _slots(page, rows)
        stamp = core.now()
        result.update(state='snapshot', printer={'name': ' '.join(page.title) or 'OpenSpoolMan'}, updated_at=stamp,
                      message='已讀取 OpenSpoolMan 槽位快照；設備在線狀態與來源更新時間未知。',
                      material_slots={'modules': modules, 'observed_at': stamp, 'source_timestamp': None,
                                      'fresh': False, 'source': 'openspoolman',
                                      'note': 'OpenSpoolMan 頁面快照；未提供印表機遙測時間或實際餘量。'})
    except _ERRORS as exc:
        result.update(error=type(exc).__name__, message='OpenSpoolMan 槽位快照目前無法讀取；設備狀態保持未知。')
    return result
