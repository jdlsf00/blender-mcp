from pathlib import Path
import tempfile

import bpy


# Minimal runtime probe: create one object and save to temp to validate bpy access.
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
if obj is None:
    raise RuntimeError("Probe failed: no active object created")

probe_output = Path(tempfile.gettempdir()) / "blender_mcp_probe.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(probe_output))
print("BLENDER_PROBE_OK")
