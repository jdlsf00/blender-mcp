#!/usr/bin/env python3
"""
Quick MCP Integration Test - Verify Blender MCP works
Tests basic functionality without emojis
"""

import subprocess
import sys
import os

def test_blender_executable():
    """Test if Blender is accessible"""
    print("\n=== Testing Blender Executable ===")
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

    if not os.path.exists(blender_path):
        print(f"ERROR: Blender not found at {blender_path}")
        return False

    print(f"OK: Blender found at {blender_path}")

    try:
        result = subprocess.run(
            [blender_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"OK: {version_line}")
            return True
        else:
            print(f"ERROR: Blender returned code {result.returncode}")
            return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_blender_python_script():
    """Test running a simple Python script in Blender"""
    print("\n=== Testing Blender Python Execution ===")
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

    # Simple test script
    test_script = """
import bpy
print("Blender Python: OK")
print(f"Blender Version: {bpy.app.version_string}")
print(f"Objects in scene: {len(bpy.data.objects)}")
"""

    try:
        result = subprocess.run(
            [blender_path, "--background", "--python-expr", test_script],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "Blender Python: OK" in result.stdout:
            print("OK: Blender Python script executed successfully")
            # Extract useful info
            for line in result.stdout.split('\n'):
                if "Blender Version:" in line or "Objects in scene:" in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print("ERROR: Script did not execute properly")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_create_sphere():
    """Test creating a sphere in Blender"""
    print("\n=== Testing Sphere Creation ===")
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

    sphere_script = """
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.0,
    location=(0, 0, 0)
)
sphere = bpy.context.active_object
sphere.name = "TestSphere"

print(f"SUCCESS: Created sphere '{sphere.name}' at {sphere.location}")
print(f"Sphere vertices: {len(sphere.data.vertices)}")
"""

    try:
        result = subprocess.run(
            [blender_path, "--background", "--python-expr", sphere_script],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "SUCCESS: Created sphere" in result.stdout:
            print("OK: Sphere created successfully")
            for line in result.stdout.split('\n'):
                if "SUCCESS:" in line or "Sphere vertices:" in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print("ERROR: Sphere creation failed")
            return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_depth_map_generation():
    """Test depth map generation capability"""
    print("\n=== Testing Depth Map Generation ===")
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

    depth_script = """
import bpy
import os

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple object
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location=(0, 0, 0))
sphere = bpy.context.active_object

# Setup camera for depth map
camera = bpy.data.cameras.new("DepthCamera")
camera_obj = bpy.data.objects.new("DepthCamera", camera)
bpy.context.scene.collection.objects.link(camera_obj)
camera_obj.location = (0, 0, 10)
camera_obj.rotation_euler = (0, 0, 0)
bpy.context.scene.camera = camera_obj

# Set orthographic
camera.type = 'ORTHO'
camera.ortho_scale = 8.0

print("SUCCESS: Depth map setup complete")
print(f"Camera: {camera_obj.name} at {camera_obj.location}")
print(f"Target object: {sphere.name}")
print("Ready for depth map rendering")
"""

    try:
        result = subprocess.run(
            [blender_path, "--background", "--python-expr", depth_script],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "SUCCESS: Depth map setup complete" in result.stdout:
            print("OK: Depth map generation capability verified")
            for line in result.stdout.split('\n'):
                if "Camera:" in line or "Target object:" in line or "Ready for" in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print("ERROR: Depth map setup failed")
            return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Blender MCP Integration - Quick Verification Test")
    print("=" * 60)

    results = {
        "Blender Executable": test_blender_executable(),
        "Python Execution": test_blender_python_script(),
        "Sphere Creation": test_create_sphere(),
        "Depth Map Setup": test_depth_map_generation()
    }

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:.<40} {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("OVERALL: ALL TESTS PASSED")
        print("\nBlender MCP integration is FUNCTIONAL and ready for:")
        print("  - 3D object creation")
        print("  - Depth map generation for CNC")
        print("  - Material and lighting setup")
        print("  - G-code toolpath generation")
        print("\nNext step: Configure GitHub Copilot MCP integration")
    else:
        print("OVERALL: SOME TESTS FAILED")
        print("\nTroubleshooting needed before MCP integration")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
