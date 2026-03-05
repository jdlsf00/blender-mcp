"""
Enable Fabex CNC addon in Blender 4.5
Run this script in Blender: blender --background --python enable_fabex.py
"""

import bpy
import sys
import addon_utils

print("\n" + "="*60)
print("FABEX CNC ADDON ENABLER")
print("="*60)

# Method 1: Try enabling as extension (Blender 4.2+)
print("\n[1] Attempting to enable Fabex as extension...")
try:
    bpy.ops.preferences.addon_enable(module='fabex')
    print("✅ Successfully enabled Fabex!")
except Exception as e:
    print(f"❌ Failed to enable: {e}")

# Method 2: Check if it's loaded
print("\n[2] Checking if Fabex is loaded...")
prefs = bpy.context.preferences
addons = prefs.addons
fabex_enabled = 'fabex' in [addon.module for addon in addons]
print(f"Fabex enabled status: {fabex_enabled}")

# Method 3: List all available modules
print("\n[3] Searching for Fabex in available modules...")
all_modules = addon_utils.modules()
fabex_found = False
for mod in all_modules:
    if 'fabex' in mod.__name__.lower():
        print(f"✅ Found module: {mod.__name__}")
        print(f"   File: {mod.__file__}")
        fabex_found = True

        # Try to enable it
        try:
            addon_utils.enable(mod.__name__)
            print(f"   Enabled: True")
        except Exception as e:
            print(f"   Enable error: {e}")

if not fabex_found:
    print("❌ Fabex module not found in available modules")

# Method 4: Check extension paths
print("\n[4] Checking extension directories...")
import os
extension_paths = [
    r"C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org",
    r"C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\scripts\addons"
]

for path in extension_paths:
    if os.path.exists(path):
        items = os.listdir(path)
        if 'fabex' in items:
            print(f"✅ Found Fabex in: {path}")
            fabex_path = os.path.join(path, 'fabex')
            manifest = os.path.join(fabex_path, 'blender_manifest.toml')
            init_py = os.path.join(fabex_path, '__init__.py')
            print(f"   - blender_manifest.toml exists: {os.path.exists(manifest)}")
            print(f"   - __init__.py exists: {os.path.exists(init_py)}")

# Save preferences
print("\n[5] Saving preferences...")
try:
    bpy.ops.wm.save_userpref()
    print("✅ Preferences saved")
except Exception as e:
    print(f"❌ Failed to save preferences: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
if fabex_enabled:
    print("✅ Fabex CNC is ENABLED and ready to use!")
    print("\nTo use Fabex:")
    print("1. Open Blender normally (not background mode)")
    print("2. Press 'N' to show right sidebar")
    print("3. Look for 'Fabex CNC' tab")
else:
    print("⚠️ Fabex is installed but NOT enabled")
    print("\nManual steps:")
    print("1. Open Blender")
    print("2. Edit → Preferences → Extensions")
    print("3. Search for 'Fabex'")
    print("4. Click checkbox to enable")

print("="*60 + "\n")

# Don't quit if running interactively
if '--background' in sys.argv:
    bpy.ops.wm.quit_blender()
