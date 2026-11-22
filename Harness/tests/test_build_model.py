import importlib.util
from pathlib import Path, PureWindowsPath


spec = importlib.util.spec_from_file_location(
    "printlab_build_model", Path(__file__).parents[1] / "build_model.py"
)
build_model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_model)


def test_relative_posix_normalizes_windows_manifest_paths():
    root = PureWindowsPath(r"C:\workspace\project")
    source = root / "Design" / "v001" / "model.py"

    assert build_model.relative_posix(source, root) == "Design/v001/model.py"
