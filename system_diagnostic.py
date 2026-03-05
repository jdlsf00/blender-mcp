#!/usr/bin/env python3
"""
Comprehensive MCP Integration System Diagnostic
Checks all components for true GitHub Copilot Pro MCP integration
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path

class MCPSystemDiagnostic:
    def __init__(self):
        self.results = {
            "system_info": {},
            "blender_status": {},
            "vscode_status": {},
            "mcp_server_status": {},
            "github_copilot_status": {},
            "integration_readiness": {},
            "recommendations": []
        }
    
    def check_system_info(self):
        """Check basic system information"""
        print("🖥️  System Information Check")
        print("=" * 40)
        
        self.results["system_info"] = {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "wsl_environment": os.path.exists("/proc/version")
        }
        
        if self.results["system_info"]["wsl_environment"]:
            try:
                with open("/proc/version", "r") as f:
                    wsl_info = f.read().strip()
                self.results["system_info"]["wsl_info"] = wsl_info
            except:
                pass
        
        for key, value in self.results["system_info"].items():
            print(f"  {key}: {value}")
        
        print("✅ System info collected\n")
    
    def check_blender_installation(self):
        """Check Blender installations"""
        print("🎨 Blender Installation Check")
        print("=" * 40)
        
        blender_paths = [
            "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe",
            "/mnt/c/Program Files/Blender Foundation/Blender 4.2/blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe"
        ]
        
        found_versions = []
        
        for path in blender_paths:
            if os.path.exists(path):
                try:
                    # Get version info
                    result = subprocess.run([path, "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version_info = result.stdout.split('\n')[0]
                        found_versions.append({
                            "path": path,
                            "version": version_info,
                            "accessible": True
                        })
                        print(f"  ✅ Found: {version_info}")
                        print(f"     Path: {path}")
                except Exception as e:
                    found_versions.append({
                        "path": path,
                        "version": "Unknown",
                        "error": str(e),
                        "accessible": False
                    })
                    print(f"  ⚠️  Found but error: {path} - {e}")
        
        if not found_versions:
            print("  ❌ No Blender installations found!")
            self.results["recommendations"].append("Install Blender 4.5 from blender.org")
        
        self.results["blender_status"] = {
            "installations_found": len(found_versions),
            "versions": found_versions,
            "latest_available": found_versions[0] if found_versions else None
        }
        print()
    
    def check_vscode_mcp_config(self):
        """Check VS Code MCP configuration"""
        print("🔧 VS Code MCP Configuration Check")
        print("=" * 40)
        
        # Check our MCP config file
        config_file = "/mnt/f/Documents/CODE/Blender-MCP/vscode_mcp_settings.json"
        config_exists = os.path.exists(config_file)
        
        print(f"  MCP Config File: {'✅ Found' if config_exists else '❌ Missing'}")
        
        if config_exists:
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                print(f"  MCP Servers Configured: {len(config_data.get('mcpServers', {}))}")
                
                if 'blender' in config_data.get('mcpServers', {}):
                    blender_config = config_data['mcpServers']['blender']
                    print(f"  ✅ Blender MCP Server: {blender_config.get('name', 'Unnamed')}")
                    print(f"     Tools: {len(blender_config.get('tools', []))}")
                    print(f"     Transport: {blender_config.get('transport', 'Unknown')}")
                else:
                    print("  ❌ Blender MCP server not configured")
                
                self.results["vscode_status"]["mcp_config"] = config_data
                
            except Exception as e:
                print(f"  ❌ Error reading config: {e}")
                self.results["vscode_status"]["config_error"] = str(e)
        
        # Check if VS Code settings might have MCP configuration
        vscode_settings_paths = [
            os.path.expanduser("~/.config/Code/User/settings.json"),
            "/mnt/c/Users/*/AppData/Roaming/Code/User/settings.json"
        ]
        
        for settings_path in vscode_settings_paths:
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, 'r') as f:
                        settings = json.load(f)
                    if 'mcp' in str(settings).lower():
                        print(f"  ✅ VS Code settings may have MCP config: {settings_path}")
                        self.results["vscode_status"]["settings_has_mcp"] = True
                        break
                except:
                    continue
        
        print()
    
    def check_mcp_server_status(self):
        """Check MCP server files and configuration"""
        print("📡 MCP Server Status Check")
        print("=" * 40)
        
        server_file = "/mnt/f/Documents/CODE/Blender-MCP/blender_mcp_server.py"
        server_exists = os.path.exists(server_file)
        
        print(f"  MCP Server File: {'✅ Found' if server_exists else '❌ Missing'}")
        
        if server_exists:
            # Count tools in server
            try:
                with open(server_file, 'r') as f:
                    content = f.read()
                
                # Count @app.tool decorators
                tool_count = content.count('@app.tool')
                print(f"  MCP Tools Defined: {tool_count}")
                
                # Check for key imports
                imports = {
                    "FastMCP": "from mcp.server.fastmcp import FastMCP" in content,
                    "bpy_operations": "blender/" in content or "import bpy" in content,
                    "async_support": "async def" in content
                }
                
                for imp, status in imports.items():
                    print(f"  {imp}: {'✅' if status else '❌'}")
                
                self.results["mcp_server_status"] = {
                    "file_exists": True,
                    "tool_count": tool_count,
                    "imports": imports
                }
                
            except Exception as e:
                print(f"  ❌ Error reading server file: {e}")
        
        # Check virtual environment
        venv_path = "/mnt/f/Documents/CODE/Blender-MCP/blender-mcp-env"
        venv_exists = os.path.exists(venv_path)
        print(f"  Virtual Environment: {'✅ Found' if venv_exists else '❌ Missing'}")
        
        if venv_exists:
            # Check for MCP dependencies
            pip_freeze_cmd = f"source {venv_path}/bin/activate && pip freeze"
            try:
                result = subprocess.run(['bash', '-c', pip_freeze_cmd], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    packages = result.stdout.lower()
                    mcp_installed = 'mcp' in packages
                    print(f"  MCP Package: {'✅ Installed' if mcp_installed else '❌ Missing'}")
                    self.results["mcp_server_status"]["mcp_package"] = mcp_installed
            except Exception as e:
                print(f"  ⚠️  Could not check packages: {e}")
        
        print()
    
    def check_github_copilot_status(self):
        """Check GitHub Copilot and VS Code integration"""
        print("🚀 GitHub Copilot Status Check")
        print("=" * 40)
        
        # Check if VS Code is running with Copilot
        try:
            result = subprocess.run(['code', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("  ✅ VS Code CLI accessible")
                vscode_version = result.stdout.split('\n')[0]
                print(f"     Version: {vscode_version}")
                self.results["github_copilot_status"]["vscode_accessible"] = True
            else:
                print("  ❌ VS Code CLI not accessible")
        except Exception as e:
            print(f"  ⚠️  VS Code check failed: {e}")
        
        # Check for Copilot extensions (common paths)
        copilot_extensions = [
            "~/.vscode/extensions/github.copilot-*",
            "~/.vscode/extensions/github.copilot-chat-*"
        ]
        
        copilot_found = False
        for ext_pattern in copilot_extensions:
            import glob
            matches = glob.glob(os.path.expanduser(ext_pattern))
            if matches:
                print(f"  ✅ Copilot extension found: {len(matches)} versions")
                copilot_found = True
                break
        
        if not copilot_found:
            print("  ⚠️  Copilot extensions not found in standard location")
        
        self.results["github_copilot_status"]["extensions_found"] = copilot_found
        print()
    
    def analyze_integration_readiness(self):
        """Analyze overall integration readiness"""
        print("🎯 Integration Readiness Analysis")
        print("=" * 40)
        
        checks = {
            "Blender 4.5+ Available": bool(self.results["blender_status"].get("installations_found", 0)),
            "MCP Server Exists": self.results["mcp_server_status"].get("file_exists", False),
            "MCP Tools Defined": self.results["mcp_server_status"].get("tool_count", 0) > 0,
            "VS Code MCP Config": bool(self.results["vscode_status"].get("mcp_config")),
            "GitHub Copilot Present": self.results["github_copilot_status"].get("extensions_found", False)
        }
        
        passed = 0
        total = len(checks)
        
        for check, status in checks.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {check}")
            if status:
                passed += 1
        
        readiness_percentage = (passed / total) * 100
        print(f"\n  Overall Readiness: {readiness_percentage:.1f}% ({passed}/{total})")
        
        if readiness_percentage >= 80:
            print("  🚀 Ready for MCP integration!")
        elif readiness_percentage >= 60:
            print("  ⚠️  Nearly ready - minor fixes needed")
        else:
            print("  ❌ Significant setup required")
        
        self.results["integration_readiness"] = {
            "checks": checks,
            "passed": passed,
            "total": total,
            "percentage": readiness_percentage
        }
        print()
    
    def generate_recommendations(self):
        """Generate specific recommendations"""
        print("💡 Recommendations")
        print("=" * 40)
        
        # Blender recommendations
        if self.results["blender_status"].get("installations_found", 0) == 0:
            self.results["recommendations"].append("Install Blender 4.5 from blender.org")
        elif any("4.5" in str(v) for v in self.results["blender_status"].get("versions", [])):
            print("  ✅ Blender 4.5 detected - ready to update MCP server config")
        else:
            self.results["recommendations"].append("Upgrade to Blender 4.5 for latest features")
        
        # MCP Server recommendations
        if not self.results["mcp_server_status"].get("mcp_package", False):
            self.results["recommendations"].append("Install MCP package: pip install mcp")
        
        # VS Code MCP recommendations
        if not self.results["vscode_status"].get("mcp_config"):
            self.results["recommendations"].append("Configure VS Code MCP settings in settings.json")
        
        # GitHub Copilot recommendations
        if not self.results["github_copilot_status"].get("extensions_found", False):
            self.results["recommendations"].append("Install GitHub Copilot Pro extension in VS Code")
        
        # Print all recommendations
        if self.results["recommendations"]:
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"  {i}. {rec}")
        else:
            print("  ✅ No immediate recommendations - system looks good!")
        
        print()
    
    def run_full_diagnostic(self):
        """Run complete system diagnostic"""
        print("🔍 MCP Integration System Diagnostic")
        print("=" * 60)
        print(f"Date: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
        print("=" * 60)
        print()
        
        self.check_system_info()
        self.check_blender_installation()
        self.check_vscode_mcp_config()
        self.check_mcp_server_status()
        self.check_github_copilot_status()
        self.analyze_integration_readiness()
        self.generate_recommendations()
        
        # Save results
        results_file = "/mnt/f/Documents/CODE/Blender-MCP/system_diagnostic_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📊 Full diagnostic results saved to: {results_file}")
        print("\n🎯 Next Steps:")
        print("1. Address any ❌ items above")
        print("2. Update Blender path to 4.5 if available")
        print("3. Enable GitHub Copilot Pro MCP functionality")
        print("4. Test end-to-end MCP integration")
        
        return self.results

if __name__ == "__main__":
    diagnostic = MCPSystemDiagnostic()
    results = diagnostic.run_full_diagnostic()