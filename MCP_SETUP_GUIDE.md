# VS Code Settings Configuration for MCP

## 🔧 **Settings.json Configuration**

Add this to your VS Code settings.json file:

```json
{
  "mcp.servers": {
    "blender": {
      "command": "wsl",
      "args": [
        "-d", 
        "Ubuntu", 
        "bash", 
        "-c", 
        "cd /mnt/f/Documents/CODE/Blender-MCP && source blender-mcp-env/bin/activate && python3 blender_mcp_server.py"
      ],
      "cwd": "f:\\Documents\\CODE\\Blender-MCP",
      "transport": "stdio"
    }
  },
  "copilot-mcp.servers": {
    "blender": {
      "command": "wsl",
      "args": [
        "-d", 
        "Ubuntu", 
        "bash", 
        "-c", 
        "cd /mnt/f/Documents/CODE/Blender-MCP && source blender-mcp-env/bin/activate && python3 blender_mcp_server.py"
      ]
    }
  },
  "mcpRunner.servers": [
    {
      "name": "blender",
      "command": "wsl -d Ubuntu bash -c \"cd /mnt/f/Documents/CODE/Blender-MCP && source blender-mcp-env/bin/activate && python3 blender_mcp_server.py\"",
      "cwd": "f:\\Documents\\CODE\\Blender-MCP"
    }
  ]
}
```

## 🎯 **Step-by-Step: Settings JSON Method**

1. **Open Command Palette**: `Ctrl+Shift+P`
2. **Type**: `Preferences: Open Settings (JSON)`
3. **Add the configuration above** to your settings
4. **Save the file**: `Ctrl+S`
5. **Restart VS Code**

## 🔍 **Finding Extension-Specific Commands**

### **Search in Command Palette**:
- Type `@ext:automatalabs.copilot-mcp` to see Copilot MCP commands
- Type `@ext:zebradev.mcp-server-runner` to see MCP Runner commands  
- Type `@ext:semanticworkbenchteam.mcp-server-vscode` to see VSCode MCP commands

### **Check Extension Documentation**:
1. **Go to Extensions** (`Ctrl+Shift+X`)
2. **Find your MCP extensions**
3. **Click on each extension**
4. **Read the documentation** for setup instructions

## 🚨 **Troubleshooting Commands Not Showing**

### **If no MCP commands appear**:
1. **Verify extensions are enabled** in Extensions panel
2. **Restart VS Code** completely
3. **Check extension compatibility** with your VS Code version
4. **Try settings.json approach** as fallback

### **Common Command Variations**:
- `MCP Server: Configure`
- `Add MCP Server`
- `Manage MCP Servers`
- `MCP: Settings`
- `Copilot MCP: Setup`

## ✅ **Quick Test Method**

After configuration, test immediately:

1. **Open GitHub Copilot Chat**: `Ctrl+Shift+I`
2. **Try**: `@mcp list tools`
3. **Or try**: `What MCP tools are available?`
4. **Should see**: List of 25+ Blender tools

## 🎯 **Expected Results**

When working correctly, you should see:
- **Tool List**: create_mesh_cube, create_material, render_image, etc.
- **Natural Language Processing**: "Create a red cube" becomes MCP tool calls
- **Mock Responses**: "✅ Mock: Created cube..." messages