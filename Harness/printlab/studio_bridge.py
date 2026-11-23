"""Session-independent, fail-closed bridge to official Bambu Studio.

Common window controls work independently of printer/feeding type. Final dispatch
is limited to the locally validated Chinese Studio build and X2D single AMS
filament on Textured PEI. It preserves an
existing Studio project by opening a separate instance. No default probe opens
windows, reserves a job, or sends a command. A Send click is evidence of dispatch,
not evidence that the printer accepted or started the job.
"""
from __future__ import annotations

import datetime as dt
import json
import hashlib
import re
import subprocess
import time
import os
import plistlib
import shutil
import tempfile
import uuid
import sys
from pathlib import Path

from . import core, bambuddy, official

STUDIO_VERSION = '02.08.02.61'
BUNDLE = '/Applications/BambuStudio.app'
# This display identity is verified alongside the selected serial, not used as a serial.
def display_name():
    value = core.config().get('studio_printer_name')
    if not isinstance(value, str) or not value.strip():
        raise core.WorkflowError('請在 Runtime/config.json 設置 Studio 中顯示的打印機名稱 studio_printer_name')
    return value.strip()


class BeforeSendError(core.WorkflowError):
    """The final-click helper was never invoked; no print command was attempted."""
    verified_not_sent = True
    command_sent = False


class HelperError(core.WorkflowError):
    """Keep the failed stage; a helper error alone never proves a Send failed."""
    def __init__(self, message, *, code='helper_failed', stage='helper'):
        super().__init__(message)
        self.code = code
        self.stage = stage


class IncompleteDeviceInfoError(core.WorkflowError):
    """The exact selected X2D still shows Studio's single-nozzle placeholder."""


HELPER_BUNDLE_ID = 'com.afang.printlab.studio-bridge'
HELPER_APP_NAME = 'PrintLab发送助手'


def _bundle_path():
    return Path('/Applications') / (HELPER_APP_NAME + '.app')


def _helper_path():
    return _bundle_path() / 'Contents/MacOS/StudioBridge'


def _build_manifest_path():
    return core.ROOT / 'Runtime/macos-build/studio-bridge-build.json'


def build_helper():
    """Build and install a dedicated local app; never requests privacy permission."""
    if sys.platform != "darwin":
        raise core.WorkflowError("發送助手構建需要 macOS。Windows 使用 docs/WINDOWS.md 中的官方 Studio 流程。")
    source = core.ROOT / 'Harness/macos/StudioBridge.swift'
    build_root = core.ROOT / 'Runtime/macos-build'
    build_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='studio-bridge-build-', dir=build_root) as temporary:
        built = Path(temporary) / (HELPER_APP_NAME + '.app')
        executable = built / 'Contents/MacOS/StudioBridge'
        executable.parent.mkdir(parents=True)
        resources = built / 'Contents/Resources'; resources.mkdir()
        subprocess.run(['/usr/bin/swiftc', str(source), '-o', str(executable)], check=True, capture_output=True, timeout=90)
        info={'CFBundleIdentifier':HELPER_BUNDLE_ID,'CFBundleName':HELPER_APP_NAME,'CFBundleDisplayName':HELPER_APP_NAME,
              'CFBundleExecutable':'StudioBridge','CFBundlePackageType':'APPL','CFBundleShortVersionString':'1.0',
              'CFBundleVersion':'1','LSMinimumSystemVersion':'14.0','LSUIElement':True,'NSHighResolutionCapable':True,
              'NSPrincipalClass':'NSApplication','NSHumanReadableCopyright':'PrintLab 本機發送橋，不包含帳號或打印機憑據'}
        icon=core.ROOT/'Harness/macos/Assets/PrintLab.icns'
        if icon.is_file():
            shutil.copy2(icon,resources/'PrintLab.icns');info['CFBundleIconFile']='PrintLab'
        (built/'Contents/Info.plist').write_bytes(plistlib.dumps(info))
        subprocess.run(['/usr/bin/codesign','--force','--sign','-','--identifier',HELPER_BUNDLE_ID,
                        '-r',f'=designated => identifier "{HELPER_BUNDLE_ID}"',str(built)],check=True,capture_output=True,timeout=20)
        subprocess.run(['/usr/bin/codesign','--verify','--deep','--strict',str(built)],check=True,capture_output=True,timeout=20)
        installed=_bundle_path()
        if installed.exists():
            backup=build_root/('StudioBridge.previous-'+uuid.uuid4().hex[:8]+'.app')
            shutil.move(str(installed),backup)
        shutil.copytree(built,installed)
    core.write_json(_build_manifest_path(), {'source_sha256':core.digest(source),'binary_sha256':core.digest(_helper_path()),
        'info_sha256':core.digest(_bundle_path()/'Contents/Info.plist'),'bundle_id':HELPER_BUNDLE_ID,'app_path':str(_bundle_path()),'built_at':core.now()})
    return _bundle_path()


def _verify_bundle():
    manifest=core.read_json(_build_manifest_path(),{})
    source=core.ROOT/'Harness/macos/StudioBridge.swift'
    if (not _helper_path().is_file() or manifest.get('source_sha256') != core.digest(source)
            or manifest.get('binary_sha256') != core.digest(_helper_path())
            or manifest.get('info_sha256') != core.digest(_bundle_path()/'Contents/Info.plist')
            or manifest.get('bundle_id') != HELPER_BUNDLE_ID):
        raise core.WorkflowError('PrintLab发送助手未安裝或發生變化，需要重新構建和驗證')
    subprocess.run(['/usr/bin/codesign','--verify','--strict',str(_bundle_path())],check=True,capture_output=True,timeout=10)


def _run(*args, timeout=20):
    """Launch through LS so TCC belongs to the helper app, never uvicorn/Python."""
    _verify_bundle()
    ipc_root=core.ROOT/'Runtime/studio-bridge-ipc'
    ipc_root.mkdir(parents=True,exist_ok=True);ipc_root.chmod(0o700)
    private=Path(tempfile.mkdtemp(prefix='request-',dir=ipc_root));private.chmod(0o700)
    receipt_read = False
    try:
        request=private/'request.json';response=private/'response.json'
        request_id=str(uuid.uuid4())
        payload=json.dumps({'request_id':request_id,'created_at':time.time(),'args':list(map(str,args))})
        fd=os.open(request,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as stream:stream.write(payload)
        deadline = time.monotonic() + timeout
        # LaunchServices -W can fail to attach to a short-lived helper. The
        # helper atomically writes its request-bound receipt after the action.
        process = subprocess.run(['/usr/bin/open','-n','-a',str(_bundle_path()),'--args','--ipc',str(request),str(response)],
                                 check=False,capture_output=True,text=True,timeout=timeout)
        while process.returncode == 0 and not response.exists() and time.monotonic() < deadline:
            time.sleep(.05)
        try:data=json.loads(response.read_text(encoding="utf-8"))
        except (OSError,ValueError,TypeError):
            detail = (process.stderr or '').strip()[:600]
            raise HelperError(f'發送助手沒有返回有效回執（退出碼 {process.returncode}）{": " + detail if detail else ""}；保留本次回執目錄：{private}', code='receipt_missing', stage='ipc') from None
        if not isinstance(data, dict):raise core.WorkflowError('發送助手回執格式無效')
        if data.get('request_id') != request_id:raise core.WorkflowError('發送助手回執不屬於本次請求')
        receipt_read = True
        if data.get('ok') is not True:
            raise HelperError(data.get('error','發送助手執行失敗'),
                              code=data.get('code','helper_failed'), stage=data.get('stage','helper'))
        if process.returncode:raise core.WorkflowError(f'發送助手啟動命令異常退出（退出碼 {process.returncode}），執行結果仍需核實')
        return data
    finally:
        # An unacknowledged helper can still be running. Keep its exact private
        # response path so a late receipt remains recoverable; never relaunch.
        if receipt_read:
            shutil.rmtree(private)


def observe_window(studio_pid, title, *, recover=False):
    """Observe/recover one exact window, independently of printer or feeding type.

    Recovery activates and restores the window once. It never clicks a Studio
    button, opens a print job, reserves a task, or requests OS permissions.
    """
    if sys.platform != 'darwin':
        raise core.WorkflowError('窗口助手需要 macOS')
    if type(studio_pid) is not int or studio_pid <= 0 or not isinstance(title, str) or not title.strip():
        raise core.WorkflowError('需要明確的 Studio 進程 ID 和完整窗口標題')
    with core.lock('studio-bridge'):
        return _run('recover-window' if recover else 'snapshot', studio_pid, title)


def window_status():
    """Read-only diagnostics without X2D, AMS, or printer-name prerequisites."""
    if sys.platform != 'darwin':
        raise core.WorkflowError('窗口助手需要 macOS')
    return _run('probe', timeout=10)


def open_preview_panel(studio_pid, title):
    """Open the preparation dialog for an exact preview; never click Send.

    This is common window control, not a declaration that this printer/feeding
    route is supported by the automatic dispatch validator.
    """
    if sys.platform != 'darwin':
        raise core.WorkflowError('窗口助手需要 macOS')
    if (type(studio_pid) is not int or studio_pid <= 0 or not isinstance(title, str)
            or not title.endswith('.gcode') or '*' in title):
        raise core.WorkflowError('需要明確的 Studio 進程 ID 和完整 .gcode 預覽窗口標題')
    observed = window_status()
    if observed.get('studio_version') != STUDIO_VERSION:
        raise core.WorkflowError('Studio 版本變更，需重新驗證界面適配器')
    with core.lock('studio-bridge'):
        return _run('open-panel', studio_pid, title)


def _launch_preview(artifact, title, before):
    """One launch, then observations only. Preserve all existing Studio instances."""
    subprocess.run(['/usr/bin/open','-n','-a',BUNDLE,'--args',str(artifact)], check=True, timeout=10)
    deadline = time.monotonic()+40
    while time.monotonic()<deadline:
        observed = _run('probe')
        matches = [i for i in observed.get('instances', []) if i['pid'] not in before
                   and any(w['title'] == title for w in i['windows'])]
        if len(matches) == 1:
            return matches[0]['pid']
        if len(matches) > 1:
            raise HelperError('Multiple new Studio instances; refusing to choose',
                              code='preview_ambiguous', stage='after_open_file')
        time.sleep(.5)
    raise HelperError('Studio did not expose the exact preview. Inspect running windows before opening another copy; no print sent',
                      code='preview_not_observed', stage='after_open_file')


def open_preview_file(path, expected_sha256):
    """Open one explicitly identified slice without changing the original project."""
    if sys.platform != 'darwin':
        raise core.WorkflowError('窗口助手需要 macOS')
    if not isinstance(path, (str, Path)) or not str(path).strip():
        raise core.WorkflowError('需要明確的 .gcode.3mf 切片文件')
    artifact = Path(path).expanduser().resolve()
    if not artifact.is_file() or not artifact.name.endswith('.gcode.3mf') or '*' in artifact.name:
        raise core.WorkflowError('需要明確的 .gcode.3mf 切片文件')
    if not isinstance(expected_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise core.WorkflowError('需要當前切片文件的 SHA-256，避免打開錯誤或變化後的文件')
    if core.digest(artifact) != expected_sha256:
        raise core.WorkflowError('Artifact changed')
    with core.lock('studio-bridge'):
        observed = window_status()
        if observed.get('studio_version') != STUDIO_VERSION:
            raise core.WorkflowError('Studio 版本變更，需重新驗證界面適配器')
        if not observed.get('accessibility') or not observed.get('screen_capture'):
            raise core.WorkflowError('PrintLab发送助手需要輔助功能和屏幕讀取權限')
        if not observed.get('session_on_console') or observed.get('screen_locked'):
            raise core.WorkflowError('需要已登錄且未鎖屏的桌面會話')
        # A CLI slice can contain editable meshes. Studio then opens Prepare
        # instead of the executable preview. Use the same byte-checked copy
        # routine as official handoff; never reslice or alter the original.
        preview_root = core.ROOT/'Runtime/studio-previews'
        preview_root.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix='preview-', dir=preview_root))
        opened = directory/artifact.name
        preservation = official.sliced_only(artifact, opened)
        if core.digest(artifact) != expected_sha256:
            raise core.WorkflowError('Artifact changed while preparing preview')
        opened_sha256 = core.digest(opened)
        core.write_json(directory/'source.json', {'source':str(artifact), 'source_sha256':expected_sha256,
                        'preview_sha256':opened_sha256, 'preservation':preservation})
        title = opened.name.removesuffix('.3mf')
        target = _launch_preview(opened, title, {i['pid'] for i in observed.get('instances', [])})
        return {'opened_preview': True, 'studio_pid': target, 'window_title': title,
                'artifact_sha256': expected_sha256, 'sent': False,
                'preview_file':str(opened), 'preview_sha256':opened_sha256,
                'preservation':preservation,
                'next': 'Inspect the exact preview; opening it does not verify printer or feeding settings.'}


def setup_permissions():
    """Explicit user-only setup action. Do not call from capability or preflight.

    Launching requests the OS dialogs; it does not grant permission or print.
    The caller should later re-run capability to observe the user's OS choices.
    """
    if sys.platform != 'darwin':
        raise core.WorkflowError('此發送助手使用 macOS 系統接口。Windows 請按 docs/WINDOWS.md 交接到官方 Studio。')
    _verify_bundle()
    subprocess.run(['/usr/bin/open','-n','-a',str(_bundle_path()),'--args','request-permissions'],
                   check=True,capture_output=True,text=True,timeout=10)
    return {'requested':True,'printed':False,'granted':None,'requires_recheck':True,
            'app_name':HELPER_APP_NAME,'app_path':str(_bundle_path()),'bundle_id':HELPER_BUNDLE_ID,
            'message':'系統將為 PrintLab发送助手 請求輔助功能和屏幕讀取權限；授權後回到工作台重新核驗。'}


def _job_supported(job):
    m = job.get('mapping', {})
    reasons = []
    if m.get('transport') != 'bambu_studio': reasons.append('需要官方 Studio 發送副本')
    if job.get('plate') != 1: reasons.append('腳本當前僅驗證單盤 plate 1')
    if m.get('use_ams') is not True or len(m.get('ams_mapping', [])) != 1: reasons.append('腳本當前僅驗證單主料 AMS 槽位')
    slots = m.get('ams_mapping', [])
    if len(slots) != 1 or type(slots[0]) is not int or not 0 <= slots[0] <= 7: reasons.append('AMS 槽位不在已驗證範圍 A1–B4')
    if len(m.get('filament_types', [])) != 1 or m['filament_types'][0] not in {'PETG', 'PLA'}: reasons.append('腳本當前僅驗證單種 PLA/PETG')
    if job.get('curr_bed_type') != 'Textured PEI Plate': reasons.append('腳本當前僅驗證紋理 PEI 板')
    if job.get('sliced_printer_model') not in {'Bambu Lab X2D', 'X2D'}: reasons.append('腳本當前僅驗證 X2D')
    return reasons


def capability(pid=None, jid=None):
    """Read-only live capability, optionally constrained to an exact job."""
    if sys.platform != 'darwin':
        message = 'Windows 使用官方 Bambu Studio 交接流程。核對具體任務並記錄批准後，在 Studio 中確認發送，步驟見 docs/WINDOWS.md。'
        return {'available': False, 'setup_supported': False, 'message': message,
                'blockers': [message], 'transport': 'bambu_studio_manual'}
    blockers = []
    try:
        display_name()
    except core.WorkflowError as exc:
        blockers.append(str(exc))
    try:
        observed = _run('probe', timeout=10)
        if observed.get('helper_bundle_id') != HELPER_BUNDLE_ID: blockers.append('發送助手未通過專用 App 身份運行')
        if observed.get('studio_version') != STUDIO_VERSION: blockers.append('Studio 版本變更，需重新驗證界面適配器')
        if not observed.get('accessibility'): blockers.append('PrintLab发送助手 尚未獲得輔助功能權限')
        if not observed.get('screen_capture'): blockers.append('PrintLab发送助手 尚未獲得屏幕讀取權限')
        if not observed.get('session_on_console') or observed.get('screen_locked'): blockers.append('需要本機已登錄且未鎖屏的桌面會話')
        if pid is not None and jid is not None:
            job = core.read_json(core.job_path(pid,jid)/'job.json')
            blockers.extend(_job_supported(job))
            if (core.job_path(pid,jid)/'HOLD-DO-NOT-PRINT.md').exists(): blockers.append('該任務仍保留暫緩打印標記；需新的啟動要求後解除，本輪不打印')
        return {'available': not blockers, 'message': '可通過本機 Studio 腳本發送；發送前仍逐項核驗窗口和具體任務' if not blockers else '；'.join(blockers),
                'blockers': blockers, 'transport': 'bambu_studio_script', 'observation': observed,
                'limitations': ['僅已驗證的中文 Studio 版本', '僅 X2D 單主料 AMS、紋理 PEI 單盤', '需要已登錄且未鎖屏桌面', '發送成功仍需設備讀回，不自動重發']}
    except (core.WorkflowError, OSError, ValueError, subprocess.SubprocessError) as exc:
        return {'available': False, 'message': str(exc), 'blockers': [str(exc)], 'transport': 'bambu_studio_script'}


def _studio_serial_matches(printer):
    config = Path.home() / 'Library/Application Support/BambuStudio/BambuStudio.conf'
    selected = core.read_json(config, {}).get('app', {}).get('user_last_selected_machine')
    return bool(printer.get('serial_number')) and selected == printer['serial_number']


def _green(token):
    # Ignore a neighboring selected button's border touching OCR bounding boxes.
    return token.get('green_pixels', 0) >= 60 and .15 < token.get('green_center_x', -1) < .85


def _validate_snapshot_identity(shot, job):
    if shot.get('title') != '发送打印任务' or shot.get('active') is not True: raise core.WorkflowError('Studio 發送窗口不是當前活動窗口')
    bounds = shot.get('bounds', {})
    ratio_x = shot.get('width', 0) / max(bounds.get('Width', 0), 1)
    ratio_y = shot.get('height', 0) / max(bounds.get('Height', 0), 1)
    if not 0.9 <= ratio_x <= 3 or abs(ratio_x-ratio_y) > .02: raise core.WorkflowError('窗口截圖與當前實際尺寸不一致')
    tokens = shot.get('tokens', [])
    texts = [t.get('text','') for t in tokens]
    if {'允许', '不允许', '打开系统设置'} & set(texts):
        raise core.WorkflowError('系統彈窗遮擋發送窗口，請先處理系統提示再繼續')
    expected = job['id'] + '.gcode'
    jobs = [s.rstrip(' /') for s in texts if re.match(r'^J\d{8}-\d{6}-[a-z0-9]+\.gcode', s)]
    if jobs != [expected]: raise core.WorkflowError('發送窗口任務名不唯一或不匹配')
    if texts.count(display_name()) != 1:
        raise core.WorkflowError('發送窗口打印機或噴嘴配置不匹配')
    models = [t.casefold() for t in texts if t.casefold().startswith('bambu lab ')]
    if models == ['bambu lab x2d 0.4mm']:
        raise IncompleteDeviceInfoError('Studio 尚未顯示完整雙噴嘴信息，需要刷新設備卡')
    if models != ['bambu lab x2d 0.4/0.4mm']:
        raise core.WorkflowError('發送窗口打印機或噴嘴配置不匹配')


def validate_snapshot(shot, job):
    """Pure validation, also exercised with observations from the real unsent dialog."""
    _validate_snapshot_identity(shot, job)
    tokens = shot.get('tokens', [])
    texts = [t.get('text', '') for t in tokens]
    m = job['mapping']; slot = m['ams_mapping'][0]
    wanted_slot = chr(ord('A')+slot//4) + str(slot%4+1)
    shown_slots = [(re.sub(r'[VvY∨▼⌄]+$', '',t['text']),t) for t in tokens if re.fullmatch(r'[A-D][1-4][VvY∨▼⌄]*', t['text'])]
    if len(shown_slots) != 1 or shown_slots[0][0] != wanted_slot: raise core.WorkflowError('AMS 槽位不匹配')
    materials = [t for t in tokens if t['text'] in {'PLA','PETG','ABS','ASA','TPU','PA','PC','Sup.PLA','Support'}]
    if len(materials) != 1 or materials[0]['text'] != m['filament_types'][0]: raise core.WorkflowError('窗口材料不匹配')
    if texts.count('PEI') != 1: raise core.WorkflowError('發送窗口未識別 PEI 板')
    for label, selected, side in [('延时摄影','关闭','left'),('动态流量校准','打开','left'),('自动热床调平','打开','right'),('喷嘴偏移校准','关闭','right')]:
        rows = [t for t in tokens if t['text'].startswith(label)]
        if len(rows) != 1: raise core.WorkflowError(f'無法核驗{label}選項')
        row = rows[0]
        options = [t for t in tokens if abs(t['y']-row['y']) < .025 and (t['x'] < .5) == (side=='left') and selected in t['text'] and _green(t)]
        # Vision sometimes joins 自動 + 打開. Green text must be in the second half.
        options = [t for t in options if t['text'] == selected or (t['text']=='自动打开' and selected=='打开' and t['green_center_x']>.60)]
        if len(options) != 1: raise core.WorkflowError(f'{label}未處於要求的{selected}狀態')
    sends = [t for t in tokens if t['text']=='发送' and t.get('confidence',0)>=.5 and _green(t) and t['y']>.85]
    if len(sends) != 1: raise core.WorkflowError('未識別唯一可用的發送按鈕')
    return {'job_id':job['id'], 'display_name':display_name(), 'slot':wanted_slot, 'filament':m['filament_types'][0], 'snapshot_sha256':shot['sha256'], 'options_verified':True}


def _open_prepared(pid,jid):
    """Reversible GUI preparation. No approval, reservation, or Send click."""
    jd = core.job_path(pid,jid); job = core.read_json(jd/'job.json')
    cap = capability(pid,jid)
    if not cap['available']: raise core.WorkflowError(cap['message'])
    artifact = core.safe_path(jd,job['artifact'])
    if core.digest(artifact) != job['artifact_sha256']: raise core.WorkflowError('Artifact changed')
    target = _launch_preview(artifact, jid+'.gcode', {i['pid'] for i in cap['observation'].get('instances',[])})
    _run('open-panel',target,jid+'.gcode')
    time.sleep(1)
    shot = _run('inspect-panel',target,'发送打印任务')
    try:
        _validate_snapshot_identity(shot, job)
    except IncompleteDeviceInfoError:
        shot = _run('refresh-printer', target, jid+'.gcode', display_name())
    try:
        proof = validate_snapshot(shot,job)
    except core.WorkflowError as exc:
        # Only the timelapse setting is changed by this adapter. Other failures
        # must remain visible before any preparation click is attempted.
        if str(exc) != '延时摄影未處於要求的关闭狀態':
            raise
        shot = _run('prepare-options',target,jid+'.gcode')
        proof = validate_snapshot(shot,job)
    return target,shot,proof


def _dispatch_impl(pid,jid,phase):
    """Send exactly once after the workbench created bound approval.

    Parent must retain its prepared-operation lock throughout this call. The
    bridge additionally owns a process-wide GUI lock. official.submit owns the
    printer ledger lock and reserves the task before the one-shot helper runs.
    """
    jd=core.job_path(pid,jid);job=core.read_json(jd/'job.json')
    if (jd/'HOLD-DO-NOT-PRINT.md').exists(): raise core.WorkflowError('This prepared job is on hold')
    if (jd/'dispatch.json').exists() or (jd/'studio-send-claimed.json').exists(): raise core.WorkflowError('Existing dispatch evidence must be reconciled; never retry automatically')
    with core.lock('studio-bridge'):
        if (jd/'dispatch.json').exists() or (jd/'studio-send-claimed.json').exists():
            raise core.WorkflowError('Existing dispatch evidence must be reconciled; never retry automatically')
        # Read-only preflight before changing application state.
        official.submit(pid,jid,execute=False)
        target,shot,proof=_open_prepared(pid,jid)
        client=bambuddy.Client()
        try:
            printer=client.get(f"printers/{job['printer_id']}")
            if not _studio_serial_matches(printer): raise core.WorkflowError('Studio selected serial does not match the approved printer')
        finally: client.close()
        core.write_json(jd/'studio-script-verification.json',{'at':core.now(), **proof, 'selected_serial_matches_printer':True,'serial_source':'Studio user_last_selected_machine plus exact dialog display identity','final_send_tested':False})
        # All lengthy GUI setup finishes before the 60-second reservation.
        phase['reservation_entered']=True
        reserved=official.submit(pid,jid,execute=True)
        if not reserved.get('reserved'): raise core.WorkflowError('Official reservation was not created')
        receipt=core.read_json(jd/'dispatch.json')
        request={'pid':target,'job_id':jid,'receipt_path':str(jd/'dispatch.json'),'artifact_path':str(jd/job['artifact']),
                 'artifact_sha256':job['artifact_sha256'],'fingerprint':receipt['fingerprint'],'snapshot_sha256':shot['sha256'],
                 'selected_serial_sha256':hashlib.sha256(printer['serial_number'].encode()).hexdigest()}
        core.write_json(jd/'studio-send-request.json',request)
        with core.lock('printer'):
            receipt=core.read_json(jd/'dispatch.json')
            try:
                phase['final_helper_invoked']=True
                result=_run('send-once',jd/'studio-send-request.json',timeout=20)
                if result.get('command_sent') is not True: raise core.WorkflowError('No verified single Send click')
                core.write_json(jd/'official-ui-send.json',{'at':core.now(),'clicked_send_once':True,'task_name':jid+'.gcode','executor':'local-studio-script','snapshot_sha256':shot['sha256']})
                receipt.update(command_sent=True,ui_send_at=core.now())
                core.write_json(jd/'dispatch.json',receipt)
                return {**result,'transport':'bambu_studio','printer_accepted':False,'next':'reconcile exact task; no automatic retry'}
            except Exception:
                # Reservation or claim may have reached the UI. Preserve uncertainty.
                # Keep existing positive observation if another reconciler completed
                # between reservation and acquiring this lock.
                if receipt.get('state') != 'observed':
                    receipt.update(state='dispatch_unknown',updated_at=core.now(),reconciliation_required=True)
                    core.write_json(jd/'dispatch.json',receipt)
                    job.update(state='dispatch_unknown',updated_at=core.now());core.write_json(jd/'job.json',job)
                raise



def dispatch(pid,jid):
    if sys.platform != 'darwin':
        raise BeforeSendError('請按 docs/WINDOWS.md 使用官方 Studio 交接流程')
    phase={'final_helper_invoked':False,'reservation_entered':False}
    try:
        return _dispatch_impl(pid,jid,phase)
    except Exception as exc:
        if not phase['final_helper_invoked'] and not phase['reservation_entered']:
            raise BeforeSendError(str(exc)) from exc
        raise
