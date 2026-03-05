import bpy

print("\n=== IMPORT OPERATORS ===")
for module_name in dir(bpy.ops):
    module = getattr(bpy.ops, module_name)
    for op_name in dir(module):
        if 'import' in op_name.lower() and 'stl' in op_name.lower():
            print(f"bpy.ops.{module_name}.{op_name}")

print("\n=== EXPORT OPERATORS ===")
for module_name in dir(bpy.ops):
    module = getattr(bpy.ops, module_name)
    for op_name in dir(module):
        if 'export' in op_name.lower() and 'stl' in op_name.lower():
            print(f"bpy.ops.{module_name}.{op_name}")

print("\n=== WM IMPORT/EXPORT ===")
for op in dir(bpy.ops.wm):
    if 'import' in op or 'export' in op:
        print(f"bpy.ops.wm.{op}")
