import copy

import httpx
import pytest

from printlab import core, material_intake, supplies


class InventoryClient:
    def __init__(self):
        self.rows = []
        self.posts = 0
        self.timeout = False
        self.persist = True

    def get(self, path):
        if path == 'inventory/spools':
            return copy.deepcopy(self.rows)
        return copy.deepcopy(next(row for row in self.rows if path == f"inventory/spools/{row['id']}"))

    def post(self, path, json):
        assert path == 'inventory/spools'
        self.posts += 1
        row = {'id': len(self.rows) + 1, **json}
        if self.persist:
            self.rows.append(row)
        if self.timeout:
            raise httpx.ReadTimeout('Simulated uncertain response')
        return copy.deepcopy(row)

    def close(self):
        pass


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(core, 'ROOT', tmp_path)
    return InventoryClient()


def register(client, request='spool-1', spool=None):
    return material_intake.register(spool or {'material': 'PLA', 'color_name': '白色'},
                                    'User confirmed this spool', request, lambda write: client)


def test_register_readback_replay_and_unknown_weight(client):
    first = register(client)
    assert not first['replayed'] and first['spool']['id'] == 1
    assert first['spool']['actual_remaining_weight'] is None
    assert first['spool']['quantity_basis'] == 'unknown'
    assert register(client)['replayed']
    assert client.posts == 1
    with pytest.raises(core.WorkflowError, match='another spool'):
        register(client, spool={'material': 'PETG'})
    second = register(client, request='spool-2')
    assert second['spool']['id'] == 2


def test_timeout_reconciles_without_second_post(client):
    client.timeout = True
    with pytest.raises(httpx.ReadTimeout):
        register(client)
    assert register(client)['replayed']
    assert client.posts == 1


def test_uncertain_empty_result_and_changed_service_do_not_retry(client):
    client.timeout, client.persist = True, False
    with pytest.raises(httpx.ReadTimeout):
        register(client)
    with pytest.raises(core.WorkflowError, match='unresolved'):
        register(client)
    assert client.posts == 1
    core.write_json(core.ROOT / 'Runtime/config.json', {'bambuddy_url': 'http://127.0.0.1:9999'})
    with pytest.raises(core.WorkflowError, match='another spool or service'):
        register(client)


def test_input_validation_and_post_registration_edits(client):
    for spool in ({'material': ''}, {'material': 'PLA', 'label_weight': -1},
                  {'material': 'PLA', 'rgba': 'white'}, {'material': 'PLA', 'access_code': 'secret'}):
        with pytest.raises(core.WorkflowError):
            register(client, spool=spool)
    assert client.posts == 0
    register(client)
    client.rows[0]['color_name'] = '黑色'
    with pytest.raises(core.WorkflowError, match='changed'):
        register(client)
    assert client.posts == 1


class Spoolman:
    def __init__(self):
        self.rows = []
        self.requests = []

    def client(self, **kwargs):
        def handle(request):
            self.requests.append((request.method, request.url.path))
            if request.method == 'GET' and request.url.path.endswith('/filament/7'):
                return httpx.Response(200, json={'id': 7, 'name': 'PLA White', 'material': 'PLA',
                                                 'weight': 1000, 'vendor': {'name': 'Bambu Lab'}})
            if request.method == 'GET' and request.url.path.endswith('/spool/100'):
                return httpx.Response(200, json=self.rows[0])
            if request.method == 'GET' and request.url.path.endswith('/spool'):
                return httpx.Response(200, json=self.rows)
            if request.method == 'POST' and request.url.path.endswith('/spool'):
                payload = request.read()
                import json
                body = json.loads(payload)
                row = {'id': 100, **body, 'filament': {'id': body['filament_id']}, 'archived': False}
                self.rows.append(row)
                return httpx.Response(200, json={'id': 100})
            return httpx.Response(404)
        return httpx.Client(base_url=kwargs.pop('base_url'), transport=httpx.MockTransport(handle), **kwargs)


@pytest.fixture
def spoolman(tmp_path, monkeypatch):
    monkeypatch.setattr(core, 'ROOT', tmp_path)
    monkeypatch.setattr(core, 'config', lambda: {'spoolman_url': 'https://spoolman.local'})
    service = Spoolman()
    monkeypatch.setattr(supplies, 'http_client', service.client)
    return service


def spoolman_input(**overrides):
    return {'spoolman_filament_id': 7, 'label_weight': 1000, 'remaining_weight': 720,
            'storage_location': 'Cabinet', **overrides}


def test_spoolman_preview_is_read_only_and_requires_confirmed_weight(spoolman):
    result = material_intake.register(spoolman_input(), 'User confirmed', 'spoolman-1', preview=True)
    assert result['state'] == 'preview'
    assert result['provider'] == 'spoolman'
    assert not any(method == 'POST' for method, _ in spoolman.requests)
    with pytest.raises(core.WorkflowError, match='remaining_weight'):
        material_intake.register({'spoolman_filament_id': 7}, 'User confirmed', 'spoolman-2', preview=True)
    assert not any(method == 'POST' for method, _ in spoolman.requests)


def test_spoolman_registration_reads_back_and_replay_is_idempotent(spoolman):
    first = material_intake.register(spoolman_input(), 'User confirmed', 'spoolman-1')
    replay = material_intake.register(spoolman_input(), 'User confirmed', 'spoolman-1')
    assert first['state'] == 'registered' and first['spool']['id'] == 100
    assert replay['replayed'] is True
    assert sum(method == 'POST' for method, _ in spoolman.requests) == 1
    assert not any(method in {'PUT', 'PATCH', 'DELETE'} for method, _ in spoolman.requests)


def test_spoolman_weight_and_retry_identity_are_validated(spoolman):
    with pytest.raises(core.WorkflowError, match='cannot exceed'):
        material_intake.register(spoolman_input(remaining_weight=1001), 'User confirmed', 'bad-weight')
    material_intake.register(spoolman_input(), 'User confirmed', 'spoolman-1')
    with pytest.raises(core.WorkflowError, match='another spool'):
        material_intake.register(spoolman_input(remaining_weight=600), 'User confirmed', 'spoolman-1')
    assert sum(method == 'POST' for method, _ in spoolman.requests) == 1
