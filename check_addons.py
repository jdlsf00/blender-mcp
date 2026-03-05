import bpy

print("\n=== Currently Enabled Addons ===")
prefs = bpy.context.preferences
for addon in prefs.addons:
    print(f"  - {addon.module}")

print("\n=== Checking for Fabex variants ===")
fabex_variants = ['fabex', 'bl_ext.blender_org.fabex', 'blender_org.fabex']
for variant in fabex_variants:
    found = variant in [a.module for a in prefs.addons]
    print(f"  {variant}: {found}")

bpy.ops.wm.quit_blender()
