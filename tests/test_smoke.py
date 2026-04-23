from blender_mcp_server import BlenderMCPServer


def test_server_initializes_tool_registry() -> None:
    server = BlenderMCPServer()
    tool_names = {tool.name for tool in server.tools}

    assert "create_cube" in tool_names
    assert "export_cam_gcode" in tool_names
    assert len(tool_names) >= 20
