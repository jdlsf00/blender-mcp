"""
Real Blender Integration Module

This module provides functionality to execute Blender operations using a real Blender installation
instead of the mock mode. It uses subprocess to run Blender in background mode with Python scripts.
"""

import subprocess
import os
import json
import tempfile
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class RealBlenderExecutor:
    """Executes Blender operations using a real Blender installation."""
    
    def __init__(self, blender_executable: str = None):
        """Initialize the Blender executor."""
        self.blender_executable = blender_executable or os.environ.get('BLENDER_EXECUTABLE')
        if not self.blender_executable:
            raise ValueError("Blender executable path not provided")
        
        # Convert WSL path to Windows path if needed
        if self.blender_executable.startswith('/mnt/c/'):
            self.blender_executable = self.blender_executable.replace('/mnt/c/', 'C:/')
        
        self.verify_blender()
    
    def verify_blender(self) -> bool:
        """Verify that Blender is accessible and working."""
        try:
            # Test Blender with a simple version check
            result = subprocess.run([
                self.blender_executable, '--version'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Blender verified: {result.stdout.split()[0]} {result.stdout.split()[1]}")
                return True
            else:
                logger.error(f"Blender verification failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify Blender: {e}")
            return False
    
    def execute_blender_script(self, script: str, blend_file: str = None) -> Dict[str, Any]:
        """Execute a Python script in Blender and return the result."""
        try:
            # Create a temporary Python script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Add result capture to the script
                wrapped_script = f"""
import bpy
import json
import sys

# Redirect output to capture results
result = {{"status": "success", "message": "", "data": None}}

try:
    # User script
{script}
    
except Exception as e:
    result["status"] = "error"
    result["message"] = str(e)
    import traceback
    result["traceback"] = traceback.format_exc()

# Write result to a file
import tempfile
result_file = "{f.name}_result.json"
with open(result_file, 'w') as rf:
    json.dump(result, rf)

print("BLENDER_MCP_RESULT:", result_file)
"""
                f.write(wrapped_script)
                script_path = f.name
            
            # Prepare Blender command
            cmd = [self.blender_executable, '--background']
            
            if blend_file:
                cmd.extend([blend_file])
            else:
                cmd.extend(['--factory-startup'])
            
            cmd.extend(['--python', script_path])
            
            # Execute Blender
            logger.info(f"Executing Blender command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Parse result
            result_data = {"status": "error", "message": "No result captured"}
            
            if "BLENDER_MCP_RESULT:" in result.stdout:
                result_file_path = result.stdout.split("BLENDER_MCP_RESULT:")[1].strip().split()[0]
                try:
                    with open(result_file_path, 'r') as rf:
                        result_data = json.load(rf)
                    os.unlink(result_file_path)  # Clean up result file
                except Exception as e:
                    logger.error(f"Failed to read result file: {e}")
            
            # Clean up script file
            os.unlink(script_path)
            
            # Add stdout/stderr to result
            result_data["stdout"] = result.stdout
            result_data["stderr"] = result.stderr
            result_data["return_code"] = result.returncode
            
            if result.returncode != 0 and result_data["status"] == "success":
                result_data["status"] = "error"
                result_data["message"] = f"Blender exited with code {result.returncode}"
            
            return result_data
            
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Blender execution timed out"}
        except Exception as e:
            logger.error(f"Failed to execute Blender script: {e}")
            return {"status": "error", "message": str(e)}

# Global instance
_blender_executor = None

def get_blender_executor() -> Optional[RealBlenderExecutor]:
    """Get the global Blender executor instance."""
    global _blender_executor
    
    if _blender_executor is None:
        blender_path = os.environ.get('BLENDER_EXECUTABLE')
        real_mode = os.environ.get('BLENDER_REAL_MODE', '').lower() == 'true'
        
        if blender_path and real_mode:
            try:
                _blender_executor = RealBlenderExecutor(blender_path)
                logger.info("Real Blender mode activated")
            except Exception as e:
                logger.warning(f"Failed to initialize real Blender mode: {e}")
                return None
        else:
            logger.info("Running in mock mode (set BLENDER_REAL_MODE=true to use real Blender)")
            return None
    
    return _blender_executor

def execute_real_blender_operation(operation_name: str, script: str) -> Dict[str, Any]:
    """Execute a Blender operation using real Blender if available, otherwise return mock result."""
    executor = get_blender_executor()
    
    if executor:
        logger.info(f"Executing real Blender operation: {operation_name}")
        return executor.execute_blender_script(script)
    else:
        logger.info(f"Mock mode: {operation_name}")
        return {"status": "mock", "message": f"Mock execution of {operation_name}"}