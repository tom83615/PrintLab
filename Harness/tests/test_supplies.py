import httpx
import pytest

from printlab import core, supplies


def spool(spool_id, remaining, archived=False):
    return {
        'id': spool_id,
        'archived': archived,
        'initial_weight': 1000,
        'remaining_weight': remaining,
        'used_weight': None if remaining is None else 1000 - remaining,
        'location': 'Cabinet',
        'filament': {
            'id': 7,
            'name': 'PLA White',
            'material': 'PLA',
            'color_hex': 'FFFFFF',
            'weight': 1000,
            'vendor': {'name': 'Bambu Lab'},
        },
    }


def test_spoolman_inventory_maps_active_spools_and_unknown_weight(monkeypatch):
    monkeypatch.setattr(core, 'config', lambda: {'spoolman_url': 'https://spoolman.local'})
    monkeypatch.setattr(supplies, '_get', lambda url: httpx.Response(200, json=[
        spool(11, None), spool(12, 420), spool(13, 500, archived=True)
    ]))

    result = supplies.inventory()

    assert result['state'] == 'online'
    assert result['source'] == 'spoolman'
    assert [item['id'] for item in result['items']] == [11, 12]
    assert result['items'][0]['remaining_weight'] is None
    assert result['items'][0]['quantity_basis'] == 'unknown'
    assert result['items'][1]['remaining_weight'] == 420
    assert result['items'][1]['quantity_basis'] == 'inventory_estimate'


def test_configured_spoolman_failure_does_not_fall_back_to_bambuddy(monkeypatch):
    monkeypatch.setattr(core, 'config', lambda: {'spoolman_url': 'https://spoolman.local'})

    def fail(_):
        raise httpx.ConnectError('offline')

    monkeypatch.setattr(supplies, '_get', fail)
    monkeypatch.setattr(supplies.bambuddy, 'inventory', lambda: pytest.fail('must not use Bambuddy'))

    result = supplies.inventory()

    assert result['state'] == 'unavailable'
    assert result['source'] == 'spoolman'
    assert 'Spoolman' in result['message']


def test_one_provider_can_be_configured_without_changing_the_other_domain(monkeypatch):
    monkeypatch.setattr(core, 'config', lambda: {'spoolman_url': 'https://spoolman.local'})
    monkeypatch.setattr(supplies, '_get', lambda _: httpx.Response(200, json=[spool(11, 500)]))
    monkeypatch.setattr(supplies.bambuddy, 'device', lambda: {'source': 'bambuddy', 'state': 'offline'})

    assert supplies.inventory()['source'] == 'spoolman'
    assert supplies.device()['source'] == 'bambuddy'

    monkeypatch.setattr(core, 'config', lambda: {'openspoolman_url': 'https://openspoolman2.local'})
    monkeypatch.setattr(supplies, '_get', lambda _: httpx.Response(200, text='''
      <div class="header"><h5>Bambu Lab H2C</h5></div>
      <div class="ams-card"><h5>AMS</h5><div class="tray-card"><div class="tray-empty">Empty</div>
      <a href="/fill?ams=0&amp;tray=0">Fill</a></div></div>'''))
    monkeypatch.setattr(supplies.bambuddy, 'inventory', lambda: {'source': 'bambuddy', 'state': 'offline'})

    assert supplies.device()['source'] == 'openspoolman'
    assert supplies.inventory()['source'] == 'bambuddy'


def test_openspoolman_slots_keep_snapshot_limits_and_duplicate_reference(monkeypatch):
    monkeypatch.setattr(core, 'config', lambda: {
        'openspoolman_url': 'https://openspoolman2.local',
        'spoolman_url': 'https://spoolman.local',
    })
    html = '''
    <div class="header"><h5>Bambu Lab H2C</h5></div>
    <div class="ams-card"><h5>AMS 2 Pro 1</h5>
      <div class="tray-card"><div class="card-header">Tray 1 - PLA</div>
        <div class="text-muted mb-2">#11</div><a href="/fill?ams=0&amp;tray=0">Fill</a></div>
      <div class="tray-card"><div class="tray-empty">Empty</div>
        <a href="/fill?ams=0&amp;tray=1">Fill</a></div>
    </div>'''

    def get(url):
        if url.endswith('/api/v1/spool'):
            return httpx.Response(200, json=[spool(11, 500), spool(12, 300)])
        return httpx.Response(200, text=html, headers={'content-type': 'text/html'})

    monkeypatch.setattr(supplies, '_get', get)
    result = supplies.device()

    assert result['state'] == 'snapshot'
    snapshot = result['material_slots']
    assert snapshot['fresh'] is False
    assert snapshot['source_timestamp'] is None
    slots = snapshot['modules'][0]['slots']
    assert slots[0]['spool_id'] == 11
    assert slots[0]['remaining_basis'] == 'unknown'
    assert slots[0]['route']['nozzle_number'] is None
    assert slots[1]['state'] == 'empty'


def test_openspoolman_duplicate_slot_cards_are_rejected(monkeypatch):
    html = '''<div class="header"><h5>Bambu Lab H2C</h5></div>
    <div class="ams-card"><h5>AMS</h5>
      <div class="tray-card"><div class="card-header">Tray 1 - PLA</div><a href="/fill?ams=0&amp;tray=0">A</a></div>
      <div class="tray-card"><div class="card-header">Tray 2 - PLA</div><a href="/fill?ams=0&amp;tray=0">B</a></div>
    </div>'''
    page = supplies._OpenSpoolPage()
    page.feed(html)
    page.close()

    with pytest.raises(ValueError, match='Duplicate'):
        supplies._slots(page, [])


def test_same_spool_referenced_by_two_slots_is_reported():
    html = '''<div class="header"><h5>Bambu Lab H2C</h5></div>
    <div class="ams-card"><h5>AMS</h5>
      <div class="tray-card"><div class="card-header">Tray 1 - PLA</div><div class="text-muted mb-2">#11</div><a href="/fill?ams=0&amp;tray=0">A</a></div>
      <div class="tray-card"><div class="card-header">Tray 2 - PLA</div><div class="text-muted mb-2">#11</div><a href="/fill?ams=0&amp;tray=1">B</a></div>
    </div>'''
    page = supplies._OpenSpoolPage()
    page.feed(html)
    page.close()

    slots = supplies._slots(page, [spool(11, 500)])[0]['slots']

    assert all(11 in slot['ledger_conflict_ids'] for slot in slots)


def test_unsupported_openspoolman_page_reports_failure_without_fallback(monkeypatch):
    monkeypatch.setattr(core, 'config', lambda: {'openspoolman_url': 'https://openspoolman2.local'})
    monkeypatch.setattr(supplies, '_get', lambda _: httpx.Response(200, text='<html><title>Changed page</title></html>'))
    monkeypatch.setattr(supplies.bambuddy, 'device', lambda: pytest.fail('must not use Bambuddy'))

    result = supplies.device()

    assert result['state'] == 'unavailable'
    assert result['source'] == 'openspoolman'
    assert result['updated_at'] is None
    assert 'OpenSpoolMan' in result['message']
