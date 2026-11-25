"""Verify separated external data root, local runtime root, and Windows CLI resolution."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def _seed_workspace_docs(data_root: Path):
    for rel, text in {
        "Context/profile.md": "# Profile\n",
        "Context/workflow.md": "# Workflow\n",
        "Context/lessons.md": "# Lessons\n",
        "Library/Devices/H2C/installed.md": "# Installed\n",
    }.items():
        path = data_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    device_card = data_root / "Library/Devices/H2C/device.json"
    device_card.write_text(
        json.dumps({"schema_version": 1, "model": "Bambu Lab H2C", "verification_status": "verified"}),
        encoding="utf-8",
    )
    (data_root / "Project").mkdir(parents=True, exist_ok=True)


def _run_cli(args, env):
    command = [sys.executable, "-X", "utf8", "-m", "printlab.cli", *args]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_split_data_and_runtime_roots_support_new_project_context_and_doctor(tmp_path):
    data_root = tmp_path / "external-data"
    runtime_root = tmp_path / "local-runtime"
    _seed_workspace_docs(data_root)
    runtime_root.mkdir(parents=True)
    (runtime_root / "config.json").write_text(
        json.dumps(
            {
                "studio_printer_name": "H2C 測試機",
                "studio_printer_model": "Bambu Lab H2C",
                "studio_printer_serial": "TEST123456789",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    env = {
        **os.environ,
        "PYTHONPATH": str(REPO_ROOT / "Harness"),
        "PRINTLAB_ROOT": str(data_root),
        "PRINTLAB_RUNTIME_ROOT": str(runtime_root),
    }

    created = _run_cli(["new", "外部空間測試作品", "--summary", "驗證分離路徑"], env)
    assert created["id"] == "P001"
    project_dir = data_root / "Project" / "P001-外部空間測試作品"
    assert (project_dir / "Review/taste-choice.example.json").is_file()
    assert (project_dir / "Review/Publication/record.json").is_file()
    assert not (data_root / "Runtime").exists()
    assert (runtime_root / "locks").is_dir()

    ctx = _run_cli(["context", "P001"], env)
    assert ctx["workspace_root"] == str(data_root.resolve())
    assert ctx["runtime_root"] == str(runtime_root.resolve())
    assert ctx["missing"] == []
    assert "AGENTS.md" in ctx["loaded"]

    status = _run_cli(["status"], env)
    assert status["workspace_root"] == str(data_root.resolve())
    assert status["runtime_root"] == str(runtime_root.resolve())
    assert [row["id"] for row in status["projects"]] == ["P001"]

    conn = _run_cli(["workspace", "connection"], env)
    assert conn["studio_printer_serial"] == "TEST123456789"
    assert conn["sha256"]

    diag = _run_cli(["doctor"], env)
    assert diag["workspace_root"] == str(data_root.resolve())
    assert diag["runtime_root"] == str(runtime_root.resolve())
    assert diag["tools"]["builder"]["available"] is True
    assert diag["printer_configured"] is True
    assert not (data_root / "Runtime").exists()


def test_windows_cli_resolves_configured_production_workspace_and_respects_override(tmp_path):
    if sys.platform != "win32":
        pytest.skip("Windows PowerShell CLI workspace resolution")

    external_data = tmp_path / "OneDrivePrintLab"
    _seed_workspace_docs(external_data)
    fake_localappdata = tmp_path / "LocalAppData"
    prod_state = fake_localappdata / "PrintLab" / "production"
    prod_runtime = prod_state / "Runtime"
    prod_runtime.mkdir(parents=True)
    (prod_state / "workspace-path.txt").write_text(str(external_data) + "\n", encoding="utf-8")
    (prod_runtime / "config.json").write_text(
        json.dumps({"studio_printer_serial": "PROD-SERIAL-001"}),
        encoding="utf-8",
    )

    cli = REPO_ROOT / "Harness/bin/printlab.ps1"
    base_env = {k: v for k, v in os.environ.items() if k not in {"PRINTLAB_ROOT", "PRINTLAB_RUNTIME_ROOT"}}
    base_env["LOCALAPPDATA"] = str(fake_localappdata)

    auto_result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(cli), "status"],
        cwd=REPO_ROOT,
        env=base_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert auto_result.returncode == 0, auto_result.stderr
    auto_data = json.loads(auto_result.stdout)
    assert auto_data["workspace_root"] == str(external_data.resolve())
    assert auto_data["runtime_root"] == str(prod_runtime.resolve())
    assert not (external_data / "Runtime").exists()

    override_dir = tmp_path / "ExplicitOverride"
    _seed_workspace_docs(override_dir)
    override_env = {**base_env, "PRINTLAB_ROOT": str(override_dir)}
    override_result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(cli), "status"],
        cwd=REPO_ROOT,
        env=override_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert override_result.returncode == 0, override_result.stderr
    override_data = json.loads(override_result.stdout)
    assert override_data["workspace_root"] == str(override_dir.resolve())
    assert override_data["runtime_root"] == str((override_dir / "Runtime").resolve())
