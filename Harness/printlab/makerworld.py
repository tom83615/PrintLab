"""Read-only synchronization of personal MakerWorld collections."""
import datetime as dt
import re
import time
from urllib.parse import urlsplit

import httpx

from . import core


SITES = {'cn': 'makerworld.com.cn', 'global': 'makerworld.com'}
API_ROOTS = {'cn': 'https://api.bambulab.cn/v1/design-service/',
             'global': 'https://makerworld.com/api/v1/design-service/'}
INTERVAL = dt.timedelta(hours=1)
PRIVATE = 'Runtime/private/makerworld.json'
MESSAGES = {
    'unconfigured': '尚未連接 MakerWorld 帳號。',
    'pending': '等待首次同步。',
    'synced': '同步成功。',
    'auth_required': 'MakerWorld 登入已失效或拒絕存取，請重新連接帳號。',
    'unavailable': 'MakerWorld 暫時無法讀取，稍後會重試。',
    'invalid_response': 'MakerWorld 收藏資料不完整或格式已變更，稍後會重試。',
}


class SyncError(core.WorkflowError):
    def __init__(self, code):
        self.code = code
        super().__init__(MESSAGES[code])


def _rows(data):
    if (not isinstance(data, dict) or type(data.get('total')) is not int
            or data['total'] < 0 or not isinstance(data.get('hits'), list)):
        raise SyncError('invalid_response')
    return data['hits'], data['total']


def _id(row):
    value = row.get('id') if isinstance(row, dict) else None
    if type(value) is not int or value <= 0:
        raise SyncError('invalid_response')
    return value


def _cover(value, site):
    if not isinstance(value, str):
        return None
    try:
        url = urlsplit(value)
        if (url.scheme == 'https' and not url.username and not url.password
                and url.port in (None, 443) and url.hostname
                and (url.hostname == site or url.hostname.endswith(
                    ('.bblmw.com', '.bblmw.cn', '.bblcdn.com', '.' + site)))):
            return value
    except ValueError:
        pass
    return None


def _fetch(region, token):
    site = SITES[region]
    with httpx.Client(base_url=API_ROOTS[region],
                      headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
                      follow_redirects=False, trust_env=False, timeout=12) as client:
        def get(path, **params):
            try:
                response = client.get(path, params=params)
                if response.headers.get('cf-mitigated') == 'challenge':
                    raise SyncError('unavailable')
                if response.status_code in (401, 403):
                    raise SyncError('auth_required')
                response.raise_for_status()
            except httpx.HTTPError:
                raise SyncError('unavailable') from None
            try:
                return response.json()
            except ValueError:
                raise SyncError('invalid_response') from None

        data = get('my/favorites/listlite')
        rows, total = _rows(data)
        collections = {_id(row): row for row in rows}
        default = data.get('default')
        if default is not None:
            collections.setdefault(_id(default), default)
        if not len(rows) <= total <= len(collections):
            raise SyncError('invalid_response')
        locale = 'zh' if region == 'cn' else 'en'
        items = {}
        folders = []
        for cid, collection in collections.items():
            label = collection.get('title')
            if not isinstance(label, str) or not label.strip():
                label = '預設收藏'
            folders.append({'id': cid, 'title': label})
            seen = set()
            expected = None
            for _ in range(200):
                time.sleep(0.3)
                page, count = _rows(get(f'favorites/{cid}/designs', limit=100, offset=len(seen)))
                if expected is not None and count != expected:
                    raise SyncError('invalid_response')
                expected = count
                for model in page:
                    mid = _id(model)
                    title = model.get('title')
                    if mid in seen or not isinstance(title, str) or not title.strip():
                        raise SyncError('invalid_response')
                    seen.add(mid)
                    author = model.get('designCreator')
                    author = author.get('name') if isinstance(author, dict) else None
                    item = items.setdefault(mid, {
                        'id': f'makerworld-{region}-{mid}', 'title': title,
                        'source_url': f'https://{site}/{locale}/models/{mid}',
                        'source_author': author if isinstance(author, str) else None,
                        'preview_url': _cover(model.get('coverUrl'), site),
                        'collection_ids': [],
                    })
                    item['collection_ids'].append(cid)
                if len(seen) == count:
                    break
                if not page or len(seen) > count:
                    raise SyncError('invalid_response')
            else:
                raise SyncError('invalid_response')
    return {'items': list(items.values()), 'collections': folders}


def _load():
    data = core.read_json(core.ROOT / PRIVATE, {})
    return data.get('credential', {}), data.get('snapshot', {})


def _save(credential, snapshot):
    core.write_json(core.ROOT / PRIVATE, {'credential': credential, 'snapshot': snapshot})


def _status(credential, snapshot):
    state = snapshot.get('state', 'pending' if credential else 'unconfigured')
    return {'state': state, 'message': MESSAGES[state], 'region': credential.get('region'),
            'last_success_at': snapshot.get('last_success_at'),
            'count': len(snapshot.get('items', []))}


def connect(region, token):
    if region not in SITES or not re.fullmatch(r'[A-Za-z0-9._~+/=-]{16,4096}', token):
        raise core.WorkflowError('請使用所選站點的有效 MakerWorld 登入憑據。')
    credential = {'region': region, 'token': token}
    with core.lock('makerworld-favorites'):
        data = _fetch(region, token)
        stamp = core.now()
        snapshot = dict(data, state='synced', attempted_at=stamp, last_success_at=stamp)
        _save(credential, snapshot)
        return _status(credential, snapshot)


def sync(force=False):
    if not (core.ROOT / PRIVATE).is_file():
        return _status({}, {})
    with core.lock('makerworld-favorites'):
        credential, snapshot = _load()
        if not credential:
            return _status({}, {})
        attempted = snapshot.get('attempted_at')
        if not force and attempted and (
            snapshot.get('state') == 'auth_required'
            or dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(attempted) < INTERVAL
        ):
            return _status(credential, snapshot)
        try:
            data = _fetch(credential['region'], credential['token'])
            snapshot.update(data, state='synced', last_success_at=core.now())
        except SyncError as exc:
            snapshot['state'] = exc.code
        snapshot['attempted_at'] = core.now()
        _save(credential, snapshot)
        return _status(credential, snapshot)


def view():
    credential, snapshot = _load()
    local = core.read_json(core.ROOT / 'Library/References/favorites.json', {})
    items = local.get('items', [])
    # Keep the local card and its notes when it already links to the same model.
    by_model = {item['source_url']: item for item in snapshot.get('items', [])}
    visible = []
    for item in items:
        url = item.get('source_url')
        if isinstance(url, str):
            match = re.fullmatch(r'https://(makerworld\.com(?:\.cn)?)/(?:[a-zA-Z-]+/)?models/(\d+)(?:[-/?#].*)?', url)
            if match:
                site, mid = match.groups()
                locale = 'zh' if site == SITES['cn'] else 'en'
                remote = by_model.pop(f'https://{site}/{locale}/models/{mid}', None)
                if remote:
                    item = dict(item, collection_ids=remote['collection_ids'])
        visible.append(item)
    return {'items': visible + list(by_model.values()), 'collections': snapshot.get('collections', []),
            'makerworld': _status(credential, snapshot)}
