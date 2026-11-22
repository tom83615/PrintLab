"""Offline route advice before permissions or task creation; never a print preflight."""
from . import core, machine_profiles


def queue_adapter_issues(model, use_ams):
    issues = []
    if not machine_profiles.single_nozzle_model(model):
        issues.append('當前隊列適配範圍為 A1、A1 mini、P1S 和 X1 Carbon。')
    if use_ams is not True:
        issues.append('PrintLab 隊列尚未適配外掛料；Bambuddy 上游支持不等於本版已接好。')
    return issues


def plan(*, model=None, feeding='unknown', permission='unknown', keep_cloud=False):
    """Use explicit facts only; presence of an AMS does not select its feeding route."""
    if feeding not in {'ams', 'external', 'unknown'} or permission not in {'unknown', 'granted', 'declined'}:
        raise core.WorkflowError('Invalid route preference')
    source = 'explicit_argument'
    if not model:
        card = core.read_json(core.DEVICE_CARD, {})
        model = card.get('user_confirmed', {}).get('model') or card.get('model')
        source = 'device_card_not_live'
    result = {
        'scope': 'setup_advice_only', 'executed': False, 'ready_to_print': False,
        'model': machine_profiles.model_id(model) or None, 'model_source': source,
        'feeding': feeding, 'permission_choice': permission,
        'preferred_route': None, 'reasons': [], 'permissions_to_recommend': [],
        'fallback': ['official_studio', 'manual_studio'],
        'before_dispatch': [
            '先核對舊任務、回執和隊列；結果未知時停止發送，不能換通道重發。',
            '按具體任務核對文件、設備、材料和清板確認，再通過統一批准與發送入口執行。',
        ],
        'limits': '僅判斷本版路線範圍；未檢查網絡、實際權限、設備狀態或切片，未修改任務。',
    }
    if not model or feeding == 'unknown':
        result.update(next_step='confirm_missing_facts',
                      reasons=['讀取已有記錄，補齊機型和本次供料方式；不能把檢測到 AMS 當作選用 AMS。'])
        return result
    issues = queue_adapter_issues(model, feeding == 'ams')
    if issues or permission == 'declined' or keep_cloud:
        result.update(preferred_route='official_studio', next_step='prepare_studio_fallback')
        result['reasons'] = issues or [
            '用戶拒絕 Bambuddy 控制授權。' if permission == 'declined'
            else '用戶要求保留雲功能；優先沿用官方 Studio，保持現有網絡模式。']
        result['studio_permissions'] = '需要自動操作時才建議對應系統權限；用戶拒絕或恢復一次仍失敗時交接人工發送。'
        return result
    result.update(preferred_route='bambuddy_queue', next_step=(
        'check_connection_readonly' if permission == 'granted' else 'explain_required_permissions'))
    result['permissions_to_recommend'] = [
        '配置專用寫入憑據，授予文件上傳、隊列管理與啟動權限；保留只讀憑據。',
        '核對機型和固件的 LAN Only / Developer Mode 要求，說明雲功能影響後由用戶選擇。',
    ] if permission == 'unknown' else []
    result['reasons'] = ['本版支持這套機型與 AMS 組合；實際發送仍須預檢和設備驗收。']
    return result
