"""Local publication review only. No network, login, upload or printer control."""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import re
import uuid
from urllib.parse import urlparse

from . import core

RECORD = "Review/Publication/record.json"
LABELS = {"checked": "已核對", "missing": "缺失", "not_allowed": "不允許", "not_applicable": "不適用"}


def template():
    return {"schema_version": 1, "intent": "local_only", "platform": "MakerWorld",
            "kind": "unknown", "revision": None, "title": "", "classification_note": "",
            "geometry_change": "unknown", "changes": [], "retained": [], "sources": [],
            "all_sources_reviewed": False, "rights_review": {}, "platform_review": {},
            "commercial_use": None, "exclusive_program": False, "output_license": {},
            "artifacts": [], "photos": [], "cover_photo": None, "target_model_url": "",
            "profile_review": {},
            "validation": {"status": "not_tested", "verified_claims": [], "unverified": []}}


def init(pid, kind="unknown"):
    p = core.project_path(pid)
    path = core.safe_path(p, RECORD, require_file=False)
    with core.project_write_lock(p):
        if path.exists():
            record = core.read_json(path)
            if not isinstance(record, dict) or record.get('schema_version') != 1:
                raise core.WorkflowError('Existing publication record is malformed; preserve it for repair')
            if record.get('intent') == 'local_only':
                record['intent'] = 'public_upload'
                if record.get('kind') == 'unknown':
                    record['kind'] = kind
                if not record.get('revision'):
                    record['revision'] = core.read_json(p / 'project.json').get('current_revision')
                core.write_json(path, record)
            return {"path": str(path), "created": False, "uploaded": False, "note": "Existing content preserved; public-upload preparation requested."}
        record = template()
        record.update(intent="public_upload", kind=kind,
                      revision=core.read_json(p / "project.json").get("current_revision"))
        core.write_json(path, record)
    return {"path": str(path), "created": True, "uploaded": False}


def _url(value):
    if not isinstance(value, str):
        return False
    u = urlparse(value)
    return u.scheme in {"http", "https"} and bool(u.hostname) and not u.username and not u.password


def _date(value):
    try:
        date = dt.date.fromisoformat(str(value))
        return date <= dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
    except ValueError:
        return False


def check(pid):
    p = core.project_path(pid)
    project = core.read_json(p / "project.json")
    path = core.safe_path(p, RECORD, require_file=False)
    record = core.read_json(path, template())
    if not isinstance(record, dict) or record.get("schema_version") != 1:
        raise core.WorkflowError("Publication record must be a schema_version=1 object")
    for key in ['rights_review', 'platform_review', 'output_license', 'validation', 'profile_review']:
        if not isinstance(record.get(key, {}), dict):
            raise core.WorkflowError(f'{key} must be an object')
    for key in ['changes', 'retained']:
        if not isinstance(record.get(key, []), list) or not all(isinstance(x, str) for x in record.get(key, [])):
            raise core.WorkflowError(f'{key} must be a list of strings')
    for key in ['verified_claims', 'unverified']:
        values = record.get('validation', {}).get(key, [])
        if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
            raise core.WorkflowError(f'validation.{key} must be a list of strings')
    rows, observed = [], {}

    def row(key, status, reason):
        rows.append({"id": key, "status": status, "label": LABELS[status], "reason": reason})

    def need(key, condition, reason):
        row(key, "checked" if condition else "missing", reason)
        return bool(condition)

    def file(ref):
        if not isinstance(ref, dict):
            return False
        rel, expected = ref.get("path"), ref.get("sha256")
        if not isinstance(rel, str) or not re.fullmatch(r"[a-f0-9]{64}", str(expected)):
            return False
        try:
            f = core.public_project_file(project["id"], rel)
            actual = core.digest(f)
            observed[rel] = actual
            return actual == expected
        except (core.WorkflowError, OSError):
            observed[rel] = None
            return False

    def review(value):
        return (isinstance(value, dict) and value.get("status") == "verified"
                and bool(value.get("note")) and _date(value.get("checked_at"))
                and file(value.get("evidence")))

    if record.get("intent") == "local_only":
        row("scope", "not_applicable", "本地設計、收藏或私人打印，不套用公開上傳門檻。")
        return {"project_id": project["id"], "status": "not_requested", "checks": rows,
                "eligible_for_confirmation": False, "upload_authorized": False, "uploaded": False}
    need("scope", record.get("intent") == "public_upload" and record.get("platform") == "MakerWorld", "明確本次僅準備MakerWorld公開上傳。")
    kind = record.get("kind")
    need("classification", kind in {"original", "remix", "print_profile"} and bool(record.get("classification_note")), "選擇原創、實質改編或僅打印配置，並說明分類依據；AI/換風格/重導出不自動變原創。")
    need("revision", bool(record.get("revision")) and record["revision"] == project.get("current_revision"), "發佈資料須綁定當前設計版本。")
    need("title", bool(record.get("title")), "填寫公開作品/配置名稱。")
    need("source_inventory", record.get("all_sources_reviewed") is True and review(record.get("rights_review")), "逐項檢查全部來源和其他第三方權利，保存核對人說明與證據；收藏不等於許可。")
    policy = record.get("platform_review", {})
    need("platform_rules", review(policy) and _url(policy.get("tutorial_url")) and _url(policy.get("community_guidelines_url")), "核對當前官方上傳教程和社區規則，受限或未讀到的細則保持待核實。")
    need("commercial_intent", type(record.get("commercial_use")) is bool, "明確是否商業用途；獨家/商業計劃另行核對和授權。")
    if record.get("exclusive_program") is not False:
        row("exclusive_program", "not_allowed", "此入口不支持參加獨家計劃；需獨立條款核對與用戶授權。")
    sources = record.get("sources", [])
    if not isinstance(sources, list):
        raise core.WorkflowError("sources must be a list")
    reused = [s for s in sources if isinstance(s, dict) and s.get("use") in {"adapted_geometry", "unchanged_geometry"}]
    if kind == "original" and reused:
        row("originality", "not_allowed", "沿用他人模型幾何不能登記為原創。")
    if kind == "remix":
        need("remix_sources", bool(reused), "改編模型必須列明原模型。")
        if record.get("geometry_change") in {"minor", "none"}:
            row("remix_substance", "not_allowed", "輕微改動/僅配色擺盤參數不算新的Remix，應使用打印配置入口或保留本地。")
        else:
            need("remix_substance", record.get("geometry_change") == "substantial" and bool(record.get("changes")) and bool(record.get("retained")), "記錄實質修改與沿用部分，並說明判斷依據。")
    if kind == "print_profile":
        need("profile_target", _url(record.get("target_model_url")), "僅打印配置須關聯原作者現有模型頁面。")
        if record.get("geometry_change") in {"minor", "substantial"}:
            row("profile_geometry", "not_allowed", "幾何已改變，不能冒充僅打印配置；先重新分類並核對許可。")
        else:
            need("profile_geometry", record.get("geometry_change") == "none" and bool(reused), "僅打印配置須明確未改變幾何，仍記錄所含模型來源與分享依據。")

    output = record.get("output_license", {})
    need("output_license", bool(output.get("name")) and _url(output.get("url")), "明確擬採用的許可；不默認Standard/原創獨家。")
    for i, source in enumerate(sources):
        key = f"source_{i + 1}"
        if not isinstance(source, dict):
            raise core.WorkflowError('Each source must be an object')
        if not isinstance(source.get('authors', []), list) or not all(isinstance(x, str) and x.strip() for x in source.get('authors', [])):
            raise core.WorkflowError('authors must be a list of names')
        if not isinstance(source.get('license', {}), dict):
            raise core.WorkflowError('Source license must be an object')
        if source.get("use") == "visual_reference":
            row(key, "not_applicable", "純視覺參考未沿用幾何；若發佈原圖/文字或實際複用模型，須改記對應權利來源並重新核對。")
            continue
        if source not in reused:
            row(key, "missing", "來源用途不明，不能假定僅作參考。")
            continue
        need(key + "_provenance", bool(source.get("authors")) and bool(source.get("title")) and _url(source.get("url"))
             and bool(source.get("version") or source.get("sha256")), "保存全部作者、原作名稱/鏈接、原文件版本或校驗值。")
        lic = source.get("license", {})
        if not isinstance(lic, dict) or not isinstance(source.get('authors', []), list) or not all(isinstance(x, str) and x for x in source.get('authors', [])):
            raise core.WorkflowError('Source license must be an object and authors a list of names')
        need(key + "_license", bool(lic.get("name")) and bool(lic.get("version")) and _url(lic.get("url"))
             and _date(lic.get("checked_at")) and file(lic.get("evidence")), "保存許可名稱、版本、原始條款鏈接、查詢日期及原文證據。")
        # Only canonical CC 4.0 URLs have mechanical defaults. Other versions/custom
        # Standard/exclusive terms require a recorded, evidence-backed assessment.
        match = re.fullmatch(r"https://creativecommons\.org/licenses/(by(?:-nc)?(?:-sa|-nd)?)/4\.0/?", str(lic.get("url")))
        if match:
            need(key + '_version', str(lic.get('version')) == '4.0', '許可版本必須與實際條款鏈接一致。')
        grant = source.get("additional_permission", {})
        bound_grant = (isinstance(grant, dict) and grant.get('source_url') == source.get('url')
                       and bool(grant.get('grantor')) and isinstance(grant.get('covers'), list)
                       and all(isinstance(x, str) for x in grant['covers']))
        granted = set(grant.get("covers", [])) if bound_grant and review(grant) else set()
        if match:
            code = match.group(1)
            allowed = {"adaptation": "-nd" not in code, "redistribution": True}
        else:
            assessed = review(lic.get("review", {}))
            allowed = lic.get("permissions", {}) if assessed else {}
            if not isinstance(allowed, dict):
                raise core.WorkflowError('License permissions must be an object')
            code = ""
        for action in ["redistribution"] + (["adaptation"] if source.get("use") == "adapted_geometry" else []):
            permitted = allowed.get(action)
            if action in granted:
                row(key + "_" + action, "checked", "額外授權已登記具體範圍及證據。")
            elif permitted is False:
                row(key + "_" + action, "not_allowed", "當前許可禁止本次公開分享/改編；署名不能代替授權，私人修改不受此上傳門檻判斷。")
            else:
                need(key + "_" + action, permitted is True, "核對本次使用和公開分享的權利；Standard/獨家等逐條核對，不憑名稱推定。")
        if "-nc" in code and record.get("commercial_use") is True and "commercial_use" not in granted:
            row(key + "_nc", "not_allowed", "NC許可與本次商業用途衝突，尚無覆蓋商業使用的額外授權。")
        if "-sa" in code and source.get("use") == "adapted_geometry":
            same = str(output.get("url", "")).rstrip("/") == str(lic.get("url", "")).rstrip("/")
            compatible = review(output.get("compatibility", {})) and source.get("url") in output["compatibility"].get("source_urls", [])
            if not same and not compatible and "license_change" not in granted:
                row(key + "_sa", "not_allowed", "SA改編須同許可或有官方兼容性依據；不得隨手改為Standard或原創獨家。")
        need(key + "_compatibility", review(source.get("output_compatibility", {})), "核對擬發佈許可與該來源、多個來源組合及本次用途兼容；保留具體依據。")
    if kind == "original" and not reused:
        row("original_author_permission", "not_applicable", "已聲明未沿用他人幾何；不索要不存在的原作者許可，其他第三方權利仍須核對。")

    artifacts = record.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise core.WorkflowError("artifacts must be a list")
    need("artifacts", bool(artifacts), "列明本次上傳文件、用途和實際SHA256。")
    hashes = set()
    profile_hashes = set()
    for i, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise core.WorkflowError('Each artifact must be an object')
        valid = file(artifact)
        need(f"file_{i + 1}", valid and artifact.get("revision") == record.get("revision") and artifact.get("role") in {"model", "print_profile"}, "上傳文件必須存在、版本一致且未被替換。")
        if valid:
            hashes.add(artifact["sha256"])
            if artifact.get("role") == "print_profile":
                profile_hashes.add(artifact["sha256"])
                try:
                    from . import project3mf
                    project3mf.inspect(core.safe_path(p, artifact["path"]))
                    row(f"profile_{i + 1}", "checked", "完整可編輯X2D工程3MF；不以僅G-code的打印包冒充平台打印配置。")
                except core.WorkflowError as e:
                    row(f"profile_{i + 1}", "missing", str(e))
    if kind == "print_profile":
        need("profile_file", bool(profile_hashes), "至少提供一個經過核對的打印配置3MF。")
    if profile_hashes:
        assessment = record.get('profile_review', {})
        comparison = assessment.get('comparison')
        if comparison in {'duplicate', 'minor_without_benefit'}:
            row('profile_value', 'not_allowed', '重複配置或無實際收益的微調不能作為新配置發佈。')
        else:
            need('profile_value', review(assessment) and comparison in {'first_profile', 'meaningful_improvement'}
                 and bool(assessment.get('benefit')), '說明首個配置或相對已有配置的實際收益，核對重複、換色/換板/換料/數量等無效微調。')
        need('profile_description', assessment.get('title_description_match') is True
             and assessment.get('time_claims_supported') is True, '核對標題、描述、耗時陳述與文件及實測對應，不作誤導或未證實保證。')
    photos = record.get("photos", [])
    if not isinstance(photos, list):
        raise core.WorkflowError("photos must be a list")
    valid_photos = []
    for i, photo in enumerate(photos):
        if not isinstance(photo, dict):
            raise core.WorkflowError('Each photo must be an object')
        valid = file(photo)
        if valid:
            with core.safe_path(p, photo["path"]).open('rb') as stream:
                header = stream.read(16)
            valid = header.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")) or (header.startswith(b"RIFF") and header[8:12] == b"WEBP")
        valid = (valid and photo.get("kind") == "real_print_photo" and photo.get("revision") == record.get("revision")
                 and photo.get("artifact_sha256") in hashes and review(photo.get("review", {}))
                 and photo.get('capture_origin') == 'own_original' and photo.get('printed_result') == 'complete'
                 and photo.get('process') == 'fdm' and photo.get('quality') == 'acceptable'
                 and photo.get('all_parts_visible') is True and photo.get('color_regions_match') is True)
        need(f"photo_{i + 1}", valid, "實拍須檢查真實來源、照片使用權、當前模型/版本/文件與所用打印配置一致，保留打印與視覺核對證據；概念/AI圖不替代實拍。")
        if valid:
            valid_photos.append(photo)
    if kind in {"original", "remix"}:
        need("real_cover", any(x.get("path") == record.get("cover_photo") for x in valid_photos), "模型封面採用已核對的真實打印照片。")
    for h in profile_hashes:
        need("profile_photo_" + h[:8], any(x.get("profile_sha256") == h for x in valid_photos), "每份打印配置至少有一張對應實物照片；僅渲染或不同配置的照片不通過。")
    validation = record.get("validation", {})
    if validation.get('status') == 'passed' and project.get('status') == 'needs_changes':
        row('validation_conflict', 'not_allowed', '項目仍需修改，不能在發佈資料中改寫為全部驗收通過。')
    need("validation", validation.get("status") in {"passed", "partial", "not_tested"}
         and bool(validation.get("unverified") or validation.get("verified_claims")), "公開說明已實測內容與未驗證部分；功能未驗收不寫已驗證。")
    if validation.get("verified_claims") or validation.get("status") in {"passed", "partial"}:
        need("validation_evidence", review(validation.get("review", {})), "實測/功能通過的陳述須有相應實物驗收證據。")
    blocked = any(x["status"] == "not_allowed" for x in rows)
    missing = any(x["status"] == "missing" for x in rows)
    status = "not_allowed" if blocked else "awaiting_evidence" if missing else "ready_for_confirmation"
    fingerprint = hashlib.sha256(json.dumps({"record": record, "observed": observed}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return {"project_id": project["id"], "status": status, "checked_at": core.now(), "checks": rows,
            "record_sha256": hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
            "fingerprint": fingerprint, "eligible_for_confirmation": not blocked and not missing,
            "upload_authorized": False, "uploaded": False, "automatic_upload_available": False}


def prepare(pid):
    """Create an immutable review packet even when evidence is missing; no upload."""
    p = core.project_path(pid)
    with core.project_write_lock(p):
        result = check(pid)
        if result["status"] == "not_requested":
            raise core.WorkflowError("No public upload requested; local designs do not need a release packet")
        record = core.read_json(p / RECORD)
        if hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True).encode()).hexdigest() != result['record_sha256']:
            raise core.WorkflowError('Publication record changed during review; check again')
        release_id = "R" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        out = core.safe_path(p, "Review/Publication/Packages/" + release_id, require_file=False)
        out.mkdir(parents=True, exist_ok=False)
        core.write_json(out / "record.json", copy.deepcopy(record))
        core.write_json(out / "check.json", result)
        lines = ["# MakerWorld 上傳前核對", "", f"狀態：{result['status']}（本地待審資料，未上傳）",
                 f"項目/版本：{result['project_id']} / {record.get('revision')}；類型：{record.get('kind')}",
                 f"標題：{record.get('title') or '【待填】'}", f"資料指紋：{result['fingerprint']}", "", "## 上傳文件與實拍", ""]
        lines += [f"- 文件：{x.get('path')}；用途：{x.get('role')}；SHA256：{x.get('sha256')}" for x in record.get('artifacts', [])]
        lines += [f"- 照片：{x.get('path')}；模型SHA256：{x.get('artifact_sha256')}；配置SHA256：{x.get('profile_sha256') or '不適用/待填'}" for x in record.get('photos', [])]
        lines += ["", "## 核對結果", ""]
        lines += [f"- {x['label']} · {x['id']}：{x['reason']}" for x in result["checks"]]
        (out / "review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        lines = ["# 公開描述草稿 · 待審", "", str(record.get("title") or "【待填標題】"), "", "## 來源與署名", ""]
        for src in record.get("sources", []):
            lic = src.get("license", {})
            lines += [f"- 原作：{src.get('title') or '【待核實】'}；作者：{', '.join(src.get('authors', [])) or '【待核實】'}",
                      f"  原作鏈接：{src.get('url') or '【待核實】'}；版本/校驗：{src.get('version') or src.get('sha256') or '【待核實】'}",
                      f"  許可：{lic.get('name') or '【待核實】'} {lic.get('version') or ''}；{lic.get('url') or '【待核實】'}；核對日期：{lic.get('checked_at') or '【待核實】'}"]
        if not record.get("sources"):
            lines.append("原創依據：" + str(record.get('classification_note') or '【待補充】') if record.get('kind') == 'original'
                         else "【複用來源待補全，不能直接刪除署名。】")
        lines += ["", "## 改動", *["- " + x for x in record.get("changes", [])], "", "## 沿用部分", *["- " + x for x in record.get("retained", [])],
                  "", "## 實際驗證", *["- 已驗證：" + x for x in record.get("validation", {}).get("verified_claims", [])],
                  *["- 未驗證：" + x for x in record.get("validation", {}).get("unverified", [])],
                  "", "## 擬發佈許可", f"{record.get('output_license', {}).get('name', '【待核實】')} {record.get('output_license', {}).get('url', '')}",
                  "", "上傳確認必須獨立取得。此資料包、設計確認、打印確認均不授權公開上傳或參加獨家/商業計劃。"]
        (out / "description-draft.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        if check(pid)['fingerprint'] != result['fingerprint']:
            raise core.WorkflowError('Publication files changed during preparation; packet is incomplete and must not be used')
        core.write_json(out / "manifest.json", {"id": release_id, "fingerprint": result["fingerprint"],
                        "files": {x.name: core.digest(x) for x in out.iterdir() if x.is_file()},
                        "uploaded": False, "upload_authorized": False})
    return {"package": str(out), "status": result["status"], "eligible_for_confirmation": result["eligible_for_confirmation"],
            "upload_authorized": False, "uploaded": False}
