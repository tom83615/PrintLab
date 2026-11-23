from threading import Event

import httpx
import pytest
from fastapi.testclient import TestClient

from printlab import api, core, makerworld


@pytest.mark.parametrize(('model', 'expected'), [
    ({'cover': 'https://makerworld.bblmw.com/cover.jpg',
      'coverUrl': 'https://makerworld.bblmw.com/legacy.jpg'}, 'cover.jpg'),
    ({'cover': 'https://elsewhere.example/cover.jpg',
      'coverUrl': 'https://makerworld.bblmw.com/legacy.jpg'}, 'legacy.jpg'),
    ({'coverPortrait': 'https://makerworld.bblmw.com/portrait.jpg'}, 'portrait.jpg'),
    ({'cover': 'https://elsewhere.example/cover.jpg',
      'coverPortrait': 'http://makerworld.bblmw.com/portrait.jpg'}, None),
])
def test_collection_cover_fields_use_trusted_https_urls(model, expected):
    url = makerworld._model_cover(model, 'makerworld.com')
    assert url == (f'https://makerworld.bblmw.com/{expected}' if expected else None)


def test_favorites_sync_reads_all_pages_and_keeps_last_complete_snapshot(tmp_path, monkeypatch):
    monkeypatch.setattr(core, 'ROOT', tmp_path)
    monkeypatch.setenv('PRINTLAB_STUDIO_PORT', '8018')
    monkeypatch.setattr(makerworld.time, 'sleep', lambda seconds: None)
    requests = []
    scenario = 'full'

    def respond(request):
        requests.append(request)
        assert request.method == 'GET'
        assert request.url.host == 'api.bambulab.cn'
        assert request.headers['authorization'] == 'Bearer sample-test-token-only'
        path = request.url.path
        if path.endswith('/listlite'):
            if scenario == 'expired':
                return httpx.Response(401)
            return httpx.Response(200, json={
                'total': 1, 'hits': [{'id': 20, 'title': '工具'}],
                'default': {'id': 10, 'title': '我的收藏'},
            })
        if path.endswith('/20/designs'):
            offset = int(request.url.params['offset'])
            if scenario == 'removed':
                return httpx.Response(200, json={'total': 0, 'hits': []})
            hits = (
                [{'id': 202, 'title': '遙控器座', 'cover': 'https://makerworld.bblmw.com/model.jpg'}] if offset else
                [{'id': 101, 'title': '螺絲起子座', 'coverUrl': 'https://elsewhere.example/cover.jpg'}]
            )
            if offset and scenario == 'partial':
                hits = []
            return httpx.Response(200, json={'total': 2, 'hits': hits})
        assert path.endswith('/10/designs')
        return httpx.Response(200, json={'total': 1, 'hits': [{'id': 101, 'title': '螺絲起子座'}]})

    client = httpx.Client
    monkeypatch.setattr(makerworld.httpx, 'Client', lambda **kw: client(transport=httpx.MockTransport(respond), **kw))
    local = {'id': 'local-1', 'title': '我選的工具座', 'reason': '要試裝',
             'source_url': 'https://makerworld.com.cn/zh/models/101-tool-holder'}
    local_path = tmp_path / 'Library/References/favorites.json'
    core.write_json(local_path, {'items': [local]})

    status = makerworld.connect('cn', 'sample-test-token-only')
    assert status['count'] == 2
    data = makerworld.view()
    assert data['items'][0] == dict(local, collection_ids=[20, 10])
    assert data['items'][1]['id'] == 'makerworld-cn-202'
    assert data['items'][1]['preview_url'] == 'https://makerworld.bblmw.com/model.jpg'
    assert 'sample-test-token-only' not in str(data)
    with TestClient(api.app, base_url='http://localhost:8018') as browser:
        response = browser.get('/api/favorites')
        assert response.json() == data
        assert response.headers['cache-control'] == 'no-store'
        assert browser.get('/api/favorites', headers={'sec-fetch-site': 'cross-site'}).status_code == 403
    assert core.read_json(local_path) == {'items': [local]}
    request_count = len(requests)
    assert makerworld.sync()['state'] == 'synced'
    assert len(requests) == request_count

    scenario = 'partial'
    assert makerworld.sync(force=True)['state'] == 'invalid_response'
    assert makerworld.view()['items'] == data['items']
    assert makerworld.view()['makerworld']['last_success_at'] == status['last_success_at']

    scenario = 'expired'
    assert makerworld.sync(force=True)['state'] == 'auth_required'
    with pytest.raises(makerworld.SyncError):
        makerworld.connect('cn', 'sample-test-token-only')
    assert makerworld.view()['items'] == data['items']

    scenario = 'removed'
    credential, snapshot = makerworld._load()
    old = dict(snapshot, state='synced', attempted_at='2000-01-01T00:00:00+00:00')
    makerworld._save(credential, old)
    saved = Event()
    save_snapshot = makerworld._save

    def notify_saved(*args):
        save_snapshot(*args)
        saved.set()

    monkeypatch.setattr(makerworld, '_save', notify_saved)
    with TestClient(api.app, base_url='http://localhost:8018') as browser:
        assert saved.wait(5)
        assert browser.get('/api/favorites').json()['makerworld']['count'] == 1
    assert makerworld.view()['items'] == [dict(local, collection_ids=[10])]
