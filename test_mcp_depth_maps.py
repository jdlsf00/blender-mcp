#!/usr/bin/env python3
"""
Test MCP Depth Map Generation with Real Blender Integration
This script demonstrates generating depth maps from the demo sculpture using our MCP server
"""

import json
import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.append('/mnt/f/Documents/CODE/Blender-MCP')

async def test_depth_map_mcp():
    """Test depth map generation through MCP integration"""
    
    print("🎯 Testing MCP Depth Map Generation")
    print("=" * 50)
    
    # First, let's create a test script that uses our MCP tools
    test_script = '''
import bpy
import sys
import os

# Add project path for imports
sys.path.append('/mnt/f/Documents/CODE/Blender-MCP')

# Import our MCP server tools directly (simulating MCP call)
from blender_mcp_server import generate_depth_map

def main():
    print("🎨 Loading demo sculpture...")
    
    # Load the demo scene
    bpy.ops.wm.open_mainfile(filepath="F:\\\\Documents\\\\Blender\\\\depth_map_demo.blend")
    
    # Verify the sculpture exists
    if "DemoSculpture" not in bpy.data.objects:
        print("❌ Demo sculpture not found!")
        return
        
    sculpture = bpy.data.objects["DemoSculpture"]
    print(f"✅ Found sculpture: {sculpture.name}")
    print(f"   Vertices: {len(sculpture.data.vertices)}")
    print(f"   Faces: {len(sculpture.data.polygons)}")
    
    # Test depth map generation with different parameters
    test_cases = [
        {
            "name": "Top View - Standard Resolution",
            "direction": "top",
            "resolution": 512,
            "format": "PNG",
            "output": "F:/Documents/Blender/depth_map_top_512.png"
        },
        {
            "name": "Front View - High Resolution", 
            "direction": "front",
            "resolution": 1024,
            "format": "TIFF",
            "output": "F:/Documents/Blender/depth_map_front_1024.tiff"
        },
        {
            "name": "Top View - CNC Ready",
            "direction": "top",
            "resolution": 2048,
            "format": "EXR",
            "invert": True,
            "output": "F:/Documents/Blender/depth_map_cnc_2048.exr"
        }
    ]
    
    print("\\n🔧 Generating depth maps...")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\\n[{i}/{len(test_cases)}] {test['name']}")
        print(f"   Direction: {test['direction']}")
        print(f"   Resolution: {test['resolution']}x{test['resolution']}")
        print(f"   Format: {test['format']}")
        
        try:
            # Call our MCP depth map tool
            result = generate_depth_map(
                object_name="DemoSculpture",
                direction=test["direction"],
                resolution=test["resolution"],
                output_path=test["output"],
                format=test["format"],
                invert=test.get("invert", False),
                depth_range=(0.0, 1.0),
                camera_distance=10.0
            )
            
            if result.get("success"):
                print(f"   ✅ Generated: {result.get('output_path')}")
                print(f"   📊 Stats: {result.get('stats', {})}")
            else:
                print(f"   ❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\\n🎯 Depth Map Generation Complete!")
    print("\\n📁 Output files:")
    for test in test_cases:
        output_file = test["output"]
        if os.path.exists(output_file.replace("F:/", "/mnt/f/")):
            size = os.path.getsize(output_file.replace("F:/", "/mnt/f/"))
            print(f"   ✅ {os.path.basename(output_file)} ({size:,} bytes)")
        else:
            print(f"   ❌ {os.path.basename(output_file)} (not found)")

if __name__ == "__main__":
    main()
'''
    
    # Write the test script
    with open("/tmp/test_mcp_depth_maps.py", "w") as f:
        f.write(test_script)
    
    print("📝 Created MCP depth map test script")
    print("🚀 Running depth map generation test...")
    
    return "/tmp/test_mcp_depth_maps.py"

if __name__ == "__main__":
    script_path = asyncio.run(test_depth_map_mcp())
    print(f"✅ Test script ready: {script_path}")