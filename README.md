# Blender MCP Server 🎨

A Model Context Protocol (MCP) server that enables **GitHub Copilot Pro** to control Blender through natural language commands in VS Code.

## 🚀 Features

- **25+ MCP Tools**: Complete Blender control through AI assistants
- **Mesh Operations**: Create and manipulate 3D objects (cubes, spheres, cylinders)  
- **Material System**: PBR materials with metallic/roughness properties
- **Scene Management**: Cameras, lighting, and scene organization
- **Animation Tools**: Keyframe animation and timeline control
- **Rendering**: Cycles, EEVEE, and Workbench render engines
- **Mock Mode**: Development without Blender installation required
- **WSL2 Ready**: Optimized for WSL2 Ubuntu environment

## 📋 Prerequisites

- **WSL2 Ubuntu** (recommended) or Python 3.12+
- **VS Code** with GitHub Copilot Pro subscription  
- **MCP Extensions** (installed during setup)

## 🛠️ Quick Setup (WSL2)

### 1. Environment Setup
```bash
# In WSL2 Ubuntu terminal
python3 -m venv blender-mcp-env
source blender-mcp-env/bin/activate
pip install mcp typing-extensions
```

### 2. Configure VS Code MCP integration
- Use the configuration patterns documented in `MCP_CONFIG.md`
- Set `BLENDER_EXECUTABLE` to your local Blender path
- Optionally set `BLENDER_SAVE_DIRECTORY` for generated `.blend` and G-code output

### 3. Test the server
```powershell
python blender_mcp_server.py
```

### Usage with GitHub Copilot Pro

Once configured, you can use natural language commands with GitHub Copilot Pro:

```
"Create a red cube at position (2, 0, 0)"
"Add a point light above the scene"
"Animate the cube to rotate 360 degrees over 100 frames"
"Render the scene with Cycles engine"
```

## MCP Tools Available

### Mesh Operations
- `create_cube` - Create cube primitives
- `create_sphere` - Create sphere primitives
- `create_cylinder` - Create cylinder primitives

### Material and Scene Operations
- `create_material` - Create a material
- `assign_material` - Assign material to an object
- `clear_scene` - Remove mesh objects from scene
- `save_blend_file` - Save current scene to `.blend`
- `render_image` - Render a still image

### CNC Toolpath Operations
- `generate_cnc_toolpath` - Generate multi-axis toolpath
- `generate_rotary_toolpath` - Generate continuous rotary path
- `optimize_toolpath` - Optimize an existing toolpath
- `export_gcode` - Export generic machine G-code
- `simulate_toolpath` - Simulate path execution
- `generate_depth_map` - Generate grayscale depth map for relief carving

### File Import/Export Operations
- `import_stl` - Import STL into Blender scene
- `export_model` - Export model as STL/OBJ/FBX/PLY

### BlenderCAM Operations
- `setup_blendercam` - Enable/configure BlenderCAM addon
- `create_cam_operation` - Create CAM operation profile
- `calculate_cam_paths` - Calculate CAM toolpaths
- `export_cam_gcode` - Export BlenderCAM G-code
- `simulate_cam_operation` - Simulate CAM material removal

## Architecture

### Mock Mode
The server includes a comprehensive mock mode that simulates Blender operations without requiring Blender installation. This enables:
- Development and testing without Blender
- CI/CD pipeline integration
- Safe operation validation

### Safety Wrappers
All Blender API calls are wrapped with safety mechanisms:
- Input validation and sanitization
- Error handling and recovery
- Mode switching (Edit/Object mode)
- Context verification

### Modular Design
Operations are organized into focused modules:
- `mesh_operations.py` - Mesh creation and modification
- `material_operations.py` - Material system integration
- `scene_operations.py` - Scene and camera management
- `animation_operations.py` - Keyframe and timeline tools
- `render_operations.py` - Rendering and output

## Development

### Project Structure
```
Blender-MCP/
├── blender_mcp_server.py          # Main MCP server
├── blender/                       # Blender operations
│   ├── __init__.py               # Module exports
│   ├── blender_utils.py          # Safety wrappers
│   ├── mesh_operations.py        # Mesh tools
│   ├── material_operations.py    # Material system
│   ├── scene_operations.py       # Scene management
│   ├── animation_operations.py   # Animation tools
│   └── render_operations.py      # Rendering
├── MCP_CONFIG.md                 # VS Code MCP config examples
├── .github/
│   └── copilot-instructions.md   # Copilot guidance
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

### Testing
```powershell
# Install test dependencies
pip install pytest black flake8

# Run tests
pytest

# Code formatting
black .

# Linting
flake8
```

### Contributing
1. Follow the safety-first development approach
2. Add comprehensive error handling
3. Include mock mode support for new operations
4. Update the MCP tool registry in `blender_mcp_server.py`
5. Test both with and without Blender installation

## Blender Integration

### Addon Installation (Future)
For deeper integration, a Blender addon will be provided that:
- Runs the MCP server within Blender
- Provides real-time synchronization
- Enables advanced features like viewport updates

### Supported Blender Versions
- Blender 3.0 LTS and newer
- Python 3.8+ compatible versions
- Both GUI and headless modes supported

## Troubleshooting

### Common Issues

1. **Python Path Issues**
   - Ensure PYTHONPATH includes the project directory
   - Use absolute paths in MCP configuration

2. **Blender Not Found**
   - Server runs in mock mode automatically
   - Install Blender for full functionality

3. **MCP Connection Issues**
   - Check your MCP server settings using `MCP_CONFIG.md`
   - Verify GitHub Copilot Pro is active
   - Restart VS Code if needed

### Logging
Enable detailed logging by setting environment variables:
```powershell
$env:MCP_LOG_LEVEL = "DEBUG"
python blender_mcp_server.py
```

## License

This project is open source. See the project repository for license details.

## Support

For issues and feature requests, please use the project's issue tracker on GitHub.