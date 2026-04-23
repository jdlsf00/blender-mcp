import importlib.util
import json
import sys
from pathlib import Path


TOOLKIT_PATH = Path(__file__).resolve().parents[1] / "fabex_workshop" / "toolkit.py"
SPEC = importlib.util.spec_from_file_location("fabex_toolkit", TOOLKIT_PATH)
assert SPEC is not None and SPEC.loader is not None
fabex_toolkit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = fabex_toolkit
SPEC.loader.exec_module(fabex_toolkit)


def test_build_coin_mold_job_outputs_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    job = fabex_toolkit.MoldJob(
        mold_type="coin",
        name="coin_38mm",
        diameter_mm=38.0,
        thickness_mm=3.2,
        material_name="wax",
    )

    written = fabex_toolkit.build_mold_job(output_dir, job)

    assert len(written) == 5
    generated = {path.name for path in written}
    assert "coin_38mm_mold.py" in generated
    assert "coin_38mm_fabex_stack.json" in generated
    assert "coin_38mm_machine_profile.json" in generated
    assert "coin_38mm_roughing.nc" in generated
    assert "coin_38mm_manifest.json" in generated

    gcode = (output_dir / "mold_jobs" / "coin_38mm" / "coin_38mm_roughing.nc").read_text(encoding="utf-8")
    assert "M3 S" in gcode
    assert "M30" in gcode

    script = (output_dir / "mold_jobs" / "coin_38mm" / "coin_38mm_mold.py").read_text(encoding="utf-8")
    assert "radius=stock_width / 2.0" in script
    assert "coin_38mm_MasterRef" in script

    manifest = json.loads((output_dir / "mold_jobs" / "coin_38mm" / "coin_38mm_manifest.json").read_text(encoding="utf-8"))
    assert manifest["job"]["mold_type"] == "coin"
    assert manifest["geometry"]["model_diameter_mm"] == 38.0


def test_build_domino_mold_job_honors_gn_flag(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    job = fabex_toolkit.MoldJob(
        mold_type="domino",
        name="domino_50x25",
        width_mm=50.0,
        height_mm=25.0,
        thickness_mm=4.0,
        corner_radius_mm=2.2,
        material_name="wax",
        use_geometry_nodes=True,
        gn_subdiv_level=2,
    )

    fabex_toolkit.build_mold_job(output_dir, job)

    script = (output_dir / "mold_jobs" / "domino_50x25" / "domino_50x25_mold.py").read_text(encoding="utf-8")
    assert "USE_GEOMETRY_NODES = True" in script
    assert "GN_SUBDIV_LEVEL = 2" in script
    assert "stock = master_outer.copy()" in script
    assert "stock_scale_x = stock_width / max(cavity_width, 1e-6)" in script

    stack = json.loads((output_dir / "mold_jobs" / "domino_50x25" / "domino_50x25_fabex_stack.json").read_text(encoding="utf-8"))
    assert stack["mold_type"] == "domino"
    assert stack["geometry_nodes"]["enabled_default"] is True


def test_build_mold_cam_batch_generates_runner_assets(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    job = fabex_toolkit.MoldJob(
        mold_type="domino",
        name="domino_cam_job",
        width_mm=48.0,
        height_mm=24.0,
        thickness_mm=3.5,
        material_name="wax",
    )
    fabex_toolkit.build_mold_job(output_dir, job)

    written = fabex_toolkit.build_mold_cam_batch(
        output_dir=output_dir,
        job_name="domino_cam_job",
        run_blender=False,
        strict_mode=True,
    )
    generated = {path.name for path in written}

    assert "domino_cam_job_cam_batch.py" in generated
    assert "domino_cam_job_run_cam_batch.ps1" in generated

    cam_script = (output_dir / "mold_jobs" / "domino_cam_job" / "domino_cam_job_cam_batch.py").read_text(encoding="utf-8")
    assert "STRICT_MODE = True" in cam_script
    assert "bpy.ops.scene.cam_operation_add()" in cam_script
    assert "bpy.ops.object.calculate_cam_path()" in cam_script
    assert "exportGcodePath" in cam_script
