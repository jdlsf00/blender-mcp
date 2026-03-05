#!/usr/bin/env python3
"""
Test script to verify MCP server communication independently of VS Code
This helps isolate whether the issue is with the server or VS Code configuration
"""
import asyncio
import json
import subprocess
import sys
from typing import Dict, Any


async def test_mcp_server():
    """Test MCP server communication using subprocess"""
    print("🧪 Testing MCP Server Connection...")
    
    # Command to start the MCP server
    cmd = [
        "wsl", "-d", "Ubuntu", "bash", "-c",
        "cd /mnt/f/Documents/CODE/Blender-MCP && source blender-mcp-env/bin/activate && python3 blender_mcp_server.py"
    ]
    
    try:
        # Start the MCP server process
        print("🚀 Starting MCP server...")
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Test 1: Initialize MCP connection
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response with timeout
        print("📥 Waiting for response...")
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print("✅ Initialize Response:", json.dumps(response, indent=2))
                
                # Test 2: List available tools
                list_tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                print("📤 Sending list tools request...")
                process.stdin.write(json.dumps(list_tools_request) + "\n")
                process.stdin.flush()
                
                tools_response_line = process.stdout.readline()
                if tools_response_line:
                    tools_response = json.loads(tools_response_line.strip())
                    print("🔧 Available Tools:")
                    if "result" in tools_response and "tools" in tools_response["result"]:
                        for tool in tools_response["result"]["tools"]:
                            print(f"  • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                        print(f"\n✅ Found {len(tools_response['result']['tools'])} tools!")
                    else:
                        print("❌ No tools found in response")
                        print("Tools Response:", json.dumps(tools_response, indent=2))
                else:
                    print("❌ No response to list tools request")
            else:
                print("❌ No response from MCP server")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Raw response: {response_line}")
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        
    finally:
        if process:
            print("🛑 Terminating MCP server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    
    print("\n" + "="*50)
    print("MCP Server Test Complete")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())