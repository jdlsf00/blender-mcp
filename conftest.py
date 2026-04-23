from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _looks_blender_runtime_script(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False

    return "import bpy" in content or "sys.exit(" in content


def pytest_ignore_collect(collection_path, config):
    path = Path(str(collection_path))

    # Keep normal pytest tests, but skip top-level Blender runtime scripts.
    if path.suffix != ".py" or not path.name.startswith("test_"):
        return False

    if path.parent != REPO_ROOT:
        return False

    return _looks_blender_runtime_script(path)
