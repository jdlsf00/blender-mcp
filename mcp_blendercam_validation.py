"""
BlenderCAM 4-Axis Validation MCP Tool
======================================

This module provides MCP tool integration for automated BlenderCAM 4-axis validation.
Wraps test_4axis_helix.py execution and returns structured metrics.

Usage:
    Call validate_4axis_helix tool with strategy and post_processor parameters.

Returns:
    JSON with A-axis count, rotation range, revolutions, CSV path, status, and errors.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

# Paths
BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
TEST_SCRIPT = Path(__file__).parent / "test_4axis_helix.py"
EXPORT_DIR = Path(__file__).parent


def validate_4axis_helix(
    strategy: str = "HELIX",
    post_processor: str = "GRBL"
) -> Dict[str, Any]:
    """
    Run BlenderCAM 4-axis validation test and return structured metrics.

    Args:
        strategy: 4-axis strategy - 'HELIX', 'PARALLEL', 'PARALLELR', 'CROSS'
        post_processor: G-code format - 'GRBL', 'ISO', 'EMC', 'MACH3'

    Returns:
        Dictionary with validation results:
        {
            "status": "SUCCESS" | "FAILED",
            "strategy": str,
            "post_processor": str,
            "a_axis_count": int,
            "total_lines": int,
            "a_axis_density": float (0.0-1.0),
            "rotation_min": float (degrees),
            "rotation_max": float (degrees),
            "rotation_avg": float (degrees),
            "total_rotation": float (degrees),
            "revolutions": float,
            "vertex_count": int,
            "calculation_time": float (seconds),
            "export_time": float (seconds),
            "csv_path": str | None,
            "gcode_path": str | None,
            "errors": list[str],
            "output": str (full console output)
        }
    """
    result = {
        "status": "FAILED",
        "strategy": strategy,
        "post_processor": post_processor,
        "a_axis_count": 0,
        "total_lines": 0,
        "a_axis_density": 0.0,
        "rotation_min": None,
        "rotation_max": None,
        "rotation_avg": None,
        "total_rotation": None,
        "revolutions": None,
        "vertex_count": None,
        "calculation_time": None,
        "export_time": None,
        "csv_path": None,
        "gcode_path": None,
        "errors": [],
        "output": ""
    }

    try:
        # Build command
        cmd = [
            str(BLENDER_EXE),
            "--background",
            "--python", str(TEST_SCRIPT),
            "--",
            "--strategy", strategy.upper(),
            "--post", post_processor.upper()
        ]

        # Run test
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120  # 2 minute timeout
        )

        output = proc.stdout + proc.stderr
        result["output"] = output

        # Parse output for metrics
        _parse_validation_output(output, result)

        # Check for test completion
        if "TEST COMPLETED SUCCESSFULLY" in output:
            result["status"] = "SUCCESS"
        elif "TEST FAILED" in output:
            result["status"] = "FAILED"
            # Extract failure reason
            for line in output.split('\n'):
                if "ERROR" in line or "FAILED" in line:
                    result["errors"].append(line.strip())

        # Locate output files
        gcode_name = f"{strategy.lower()}_test_4axis.gcode"
        csv_name = f"{strategy.lower()}_test_4axis.csv"

        gcode_path = EXPORT_DIR / gcode_name
        csv_path = EXPORT_DIR / csv_name

        if gcode_path.exists():
            result["gcode_path"] = str(gcode_path)
        if csv_path.exists():
            result["csv_path"] = str(csv_path)

    except subprocess.TimeoutExpired:
        result["errors"].append("Test execution timed out (>120s)")
    except FileNotFoundError:
        result["errors"].append(f"Blender executable not found: {BLENDER_EXE}")
    except Exception as e:
        result["errors"].append(f"Execution error: {str(e)}")

    return result


def _parse_validation_output(output: str, result: Dict[str, Any]) -> None:
    """
    Parse validation test output and extract metrics.

    Args:
        output: Console output from test script
        result: Dictionary to populate with parsed metrics
    """
    # Extract A-axis statistics
    if match := re.search(r'Total lines:\s*(\d+)', output):
        result["total_lines"] = int(match.group(1))

    if match := re.search(r'Lines with A-axis:\s*(\d+)', output):
        result["a_axis_count"] = int(match.group(1))

    # Calculate density
    if result["total_lines"] > 0:
        result["a_axis_density"] = result["a_axis_count"] / result["total_lines"]

    # Extract rotation statistics
    if match := re.search(r'Min:\s*([\d.]+)°', output):
        result["rotation_min"] = float(match.group(1))

    if match := re.search(r'Max:\s*([\d.]+)°', output):
        result["rotation_max"] = float(match.group(1))

    if match := re.search(r'Avg:\s*([\d.]+)°', output):
        result["rotation_avg"] = float(match.group(1))

    if match := re.search(r'Total rotation:\s*([\d.]+)°', output):
        result["total_rotation"] = float(match.group(1))

    if match := re.search(r'Full revolutions:\s*([\d.]+)', output):
        result["revolutions"] = float(match.group(1))

    # Extract vertex count
    if match := re.search(r'Path mesh created:\s*(\d+)\s*vertices', output):
        result["vertex_count"] = int(match.group(1))

    # Extract timing
    if match := re.search(r'Toolpath calculation complete \(([\d.]+)s\)', output):
        result["calculation_time"] = float(match.group(1))


def run_batch_validation(
    strategies: Optional[list[str]] = None,
    post_processors: Optional[list[str]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Run validation tests for multiple strategy/post-processor combinations.

    Args:
        strategies: List of strategies to test (default: all)
        post_processors: List of post-processors to test (default: all)

    Returns:
        Dictionary mapping "STRATEGY_POST" to validation results
    """
    if strategies is None:
        strategies = ["HELIX", "PARALLEL", "PARALLELR", "CROSS"]
    if post_processors is None:
        post_processors = ["GRBL", "ISO", "EMC", "MACH3"]

    results = {}

    for strategy in strategies:
        for post in post_processors:
            key = f"{strategy}_{post}"
            print(f"Running validation: {key}...")
            results[key] = validate_4axis_helix(strategy, post)

    return results


def export_batch_summary(results: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    """
    Export batch validation results to JSON summary file.

    Args:
        results: Dictionary from run_batch_validation()
        output_path: Path to write JSON summary
    """
    summary = {
        "test_date": "2025-11-12",
        "blender_version": "4.5.3 LTS",
        "test_count": len(results),
        "results": results
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"Batch summary exported: {output_path}")


# MCP Tool Definition (for reference)
MCP_TOOL_SCHEMA = {
    "name": "validate_4axis_helix",
    "description": "Run BlenderCAM 4-axis validation test and return structured metrics",
    "inputSchema": {
        "type": "object",
        "properties": {
            "strategy": {
                "type": "string",
                "enum": ["HELIX", "PARALLEL", "PARALLELR", "CROSS"],
                "default": "HELIX",
                "description": "4-axis machining strategy to test"
            },
            "post_processor": {
                "type": "string",
                "enum": ["GRBL", "ISO", "EMC", "MACH3"],
                "default": "GRBL",
                "description": "G-code post-processor format"
            }
        }
    }
}


if __name__ == "__main__":
    # Example: Run single test
    print("Running HELIX validation with GRBL...")
    result = validate_4axis_helix("HELIX", "GRBL")

    print(f"\nStatus: {result['status']}")
    print(f"A-axis density: {result['a_axis_density']*100:.2f}%")
    print(f"Rotation: {result['rotation_min']}° → {result['rotation_max']}°")
    print(f"Revolutions: {result['revolutions']:.2f}")
    print(f"CSV: {result['csv_path']}")

    if result['errors']:
        print("\nErrors:")
        for err in result['errors']:
            print(f"  - {err}")
