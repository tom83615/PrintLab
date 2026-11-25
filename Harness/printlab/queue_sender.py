"""Workbench access to the existing single-dispatch Bambuddy queue adapter."""
from . import bambuddy, core, dispatch_plan


def capability(report):
    blockers = []
    pid, jid = report.get('project_id'), report.get('job_id')
    if not pid or not jid:
        return {'available': False, 'kind': 'bambuddy_queue', 'message': '請選擇已綁定具體設備的待打印任務'}
    job = core.read_json(core.job_path(pid, jid) / 'job.json')
    blockers.extend(dispatch_plan.queue_adapter_issues(
        job.get('sliced_printer_model'), job.get('mapping', {}).get('use_ams')))
    if job.get('mapping', {}).get('transport') != 'bambuddy_queue':
        blockers.append('任務尚未明確綁定 Bambuddy 隊列通道')
    if report.get('device', {}).get('state') != 'IDLE':
        blockers.append('隊列通道需要設備就緒為 IDLE；請核對上一盤與設備狀態')
    if report.get('transport', {}).get('sdcard') is not True:
        blockers.append('設備未報告可用存儲卡，文件傳輸條件待核對')
    secret = core.read_json(core.runtime_root() / 'private/bambuddy.json', {})
    if not secret.get('write_api_key'):
        blockers.append('Bambuddy 寫入憑據尚未配置，需具備文件、隊列和啟動權限')
    return {'available': not blockers, 'kind': 'bambuddy_queue', 'blockers': blockers,
            'message': '；'.join(blockers) if blockers else '可嘗試通過 Bambuddy 隊列發送，設備接受結果須另行讀回',
            'independent_dispatch_verified': False,
            'limitations': ['實際接收取決於設備固件及當前連接權限', '發送結果未知時先對帳', '僅已核對的具體任務可啟動']}


def dispatch(pid, jid):
    # This reuses approval, file binding, durable upload/start receipts and the printer lock.
    # An exception after any attempted write is handled as uncertain by the workbench.
    receipt_path = core.job_path(pid, jid) / 'dispatch.json'
    try:
        result = bambuddy.submit(pid, jid, execute=True)
    except Exception as exc:
        if not receipt_path.exists():
            from .studio_bridge import BeforeSendError
            raise BeforeSendError(str(exc)) from exc
        raise
    receipt = core.read_json(receipt_path, {})
    return {'command_sent': bool(receipt.get('start_requested_at')), 'executed': False,
            'transport': 'bambuddy_queue', 'queue_id': receipt.get('queue_id'),
            'printer_accepted': result.get('matching_task') is True and result.get('fresh') is True}
