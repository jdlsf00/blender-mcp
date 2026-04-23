from pathlib import Path
import os
import subprocess

import pytest


def resolve_blender_executable() -> str | None:
    env_path = os.getenv("BLENDER_EXECUTABLE")
    if env_path and os.path.exists(env_path):
        return env_path

    candidates = [
        r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
        "/mnt/c/Program Files/Blender Foundation/Blender 5.1/blender.exe",
        "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe",
    ]

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return None


@pytest.mark.blender
def test_blender_background_probe() -> None:
    blender_exe = resolve_blender_executable()
    if not blender_exe:
        pytest.skip("No Blender executable found. Set BLENDER_EXECUTABLE to run Blender integration tests.")

    probe_script = Path(__file__).with_name("blender_probe.py")
    cmd = [
        blender_exe,
        "--background",
        "--factory-startup",
        "--python",
        str(probe_script),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    combined_output = (result.stdout or "") + "\n" + (result.stderr or "")

    assert result.returncode == 0, (
        f"Blender probe failed with exit code {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "BLENDER_PROBE_OK" in combined_output
