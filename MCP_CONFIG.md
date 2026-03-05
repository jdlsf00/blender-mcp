# MCP Server Configuration Guide

## 🔧 **VS Code MCP Extension Settings**

### **Configuration Format 1: Command + Arguments**
```json
{
  "name": "blender",
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
```

### **Configuration Format 2: Single Command Line**
```json
{
  "name": "blender",
  "command": "wsl -d Ubuntu bash -c \"cd /mnt/f/Documents/CODE/Blender-MCP && source blender-mcp-env/bin/activate && python3 blender_mcp_server.py\"",
  "transport": "stdio",
  "cwd": "f:\\Documents\\CODE\\Blender-MCP"
}
```

### **Configuration Format 3: Simple Form Fields**

**Server Name:** `blender`

**Command:** `wsl`

**Arguments (single line):**
```
-d Ubuntu bash -c "cd /mnt/f/Documents/CODE/Blender-MCP && source blender-mcp-env/bin/activate && python3 blender_mcp_server.py"
```

**Port:** (leave empty or enter `null`)

**Transport:** `stdio` (if available)

**Working Directory:** `f:\Documents\CODE\Blender-MCP`

## 🎯 **Key Points**

1. **No Port Needed**: MCP servers use STDIO, not network ports
2. **WSL Path**: Use `/mnt/f/Documents/CODE/Blender-MCP` inside WSL
3. **Virtual Environment**: Must activate `blender-mcp-env` before running
4. **Transport**: Always `stdio` for VS Code integration

## 🔍 **Verification Commands**

After configuration, test with these GitHub Copilot commands:

```
@mcp list available tools
```

```
Create a simple red cube
```

Expected response should show MCP tools or mock cube creation.

## 🚨 **Troubleshooting**

**If server won't start:**
- Verify WSL Ubuntu is running: `wsl -l -v`
- Check path exists in WSL: `wsl -d Ubuntu ls /mnt/f/Documents/CODE/Blender-MCP`
- Test manual startup: Run the full command in terminal

**If tools don't appear:**
- Restart VS Code after configuration
- Check GitHub Copilot Pro subscription is active
- Verify MCP extension is enabled