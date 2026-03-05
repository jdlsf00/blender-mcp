"""
BlenderCAM 4-Axis Batch Test Runner
====================================

Runs validation tests across multiple strategy/post-processor combinations
and generates comprehensive comparison report.

Usage:
    python batch_test_runner.py [--strategies HELIX,PARALLELR] [--posts GRBL,ISO]

    # Run all combinations (default)
    python batch_test_runner.py

    # Run specific subset
    python batch_test_runner.py --strategies HELIX --posts GRBL,ISO,EMC,MACH3
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import MCP validation module
from mcp_blendercam_validation import validate_4axis_helix, export_batch_summary


def run_batch_tests(
    strategies: List[str],
    post_processors: List[str],
    output_dir: Path = None
) -> Dict[str, Any]:
    """
    Run validation tests for all strategy/post-processor combinations.

    Args:
        strategies: List of strategies to test
        post_processors: List of post-processors to test
        output_dir: Directory to save results (default: current directory)

    Returns:
        Dictionary with batch test results and summary statistics
    """
    if output_dir is None:
        output_dir = Path(__file__).parent

    print("=" * 80)
    print("BlenderCAM 4-Axis Batch Validation")
    print("=" * 80)
    print(f"Strategies: {', '.join(strategies)}")
    print(f"Post-processors: {', '.join(post_processors)}")
    print(f"Total tests: {len(strategies) * len(post_processors)}")
    print("=" * 80 + "\n")

    results = {}
    success_count = 0
    failure_count = 0

    for i, strategy in enumerate(strategies, 1):
        for j, post in enumerate(post_processors, 1):
            test_num = (i - 1) * len(post_processors) + j
            total_tests = len(strategies) * len(post_processors)

            print(f"[{test_num}/{total_tests}] Testing {strategy} + {post}...")

            result = validate_4axis_helix(strategy, post)
            key = f"{strategy}_{post}"
            results[key] = result

            if result["status"] == "SUCCESS":
                success_count += 1
                print(f"  ✅ SUCCESS - A-axis: {result['a_axis_density']*100:.2f}%, "
                      f"Rotations: {result['revolutions']:.2f}")
            else:
                failure_count += 1
                print(f"  ❌ FAILED - {result['errors'][0] if result['errors'] else 'Unknown error'}")

            print()

    # Generate summary
    summary = {
        "test_date": datetime.now().isoformat(),
        "blender_version": "4.5.3 LTS",
        "strategies_tested": strategies,
        "post_processors_tested": post_processors,
        "total_tests": len(results),
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": success_count / len(results) if results else 0,
        "results": results
    }

    # Print summary table
    print_summary_table(summary)

    # Export to JSON
    summary_path = output_dir / f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\n📊 Batch results saved: {summary_path}")

    return summary


def print_summary_table(summary: Dict[str, Any]) -> None:
    """Print formatted summary table of batch test results."""
    print("\n" + "=" * 80)
    print("BATCH TEST SUMMARY")
    print("=" * 80)
    print(f"Test Date: {summary['test_date']}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Success: {summary['success_count']} ({summary['success_rate']*100:.1f}%)")
    print(f"Failed: {summary['failure_count']}")
    print("\n" + "-" * 80)
    print(f"{'Strategy':<15} {'Post':<10} {'Status':<10} {'A-Axis %':<12} {'Rotations':<12}")
    print("-" * 80)

    for key, result in summary['results'].items():
        strategy, post = key.split('_')
        status_icon = "✅" if result['status'] == "SUCCESS" else "❌"

        a_axis_pct = f"{result['a_axis_density']*100:.2f}%" if result['a_axis_density'] else "N/A"
        revolutions = f"{result['revolutions']:.2f}" if result['revolutions'] else "N/A"

        print(f"{strategy:<15} {post:<10} {status_icon:<10} {a_axis_pct:<12} {revolutions:<12}")

    print("=" * 80 + "\n")


def generate_markdown_report(summary: Dict[str, Any], output_path: Path) -> None:
    """
    Generate markdown report from batch test results.

    Args:
        summary: Batch test summary dictionary
        output_path: Path to write markdown report
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# BlenderCAM 4-Axis Batch Test Report\n\n")
        f.write(f"**Test Date:** {summary['test_date']}  \n")
        f.write(f"**Blender Version:** {summary['blender_version']}  \n")
        f.write(f"**Total Tests:** {summary['total_tests']}  \n")
        f.write(f"**Success Rate:** {summary['success_rate']*100:.1f}%  \n\n")

        f.write("## Summary Table\n\n")
        f.write("| Strategy | Post-Processor | Status | A-Axis Density | Rotations | CSV |\n")
        f.write("|----------|----------------|--------|----------------|-----------|-----|\n")

        for key, result in summary['results'].items():
            strategy, post = key.split('_')
            status = "✅" if result['status'] == "SUCCESS" else "❌"
            density = f"{result['a_axis_density']*100:.2f}%" if result['a_axis_density'] else "N/A"
            revs = f"{result['revolutions']:.2f}" if result['revolutions'] else "N/A"
            csv = "✅" if result['csv_path'] else "❌"

            f.write(f"| {strategy} | {post} | {status} | {density} | {revs} | {csv} |\n")

        f.write("\n## Detailed Results\n\n")

        for key, result in summary['results'].items():
            strategy, post = key.split('_')
            f.write(f"### {strategy} + {post}\n\n")

            if result['status'] == "SUCCESS":
                f.write(f"**Status:** ✅ SUCCESS  \n")
                f.write(f"**A-axis lines:** {result['a_axis_count']} / {result['total_lines']} "
                       f"({result['a_axis_density']*100:.2f}%)  \n")
                f.write(f"**Rotation range:** {result['rotation_min']:.3f}° → "
                       f"{result['rotation_max']:.3f}°  \n")
                f.write(f"**Total rotation:** {result['total_rotation']:.3f}° "
                       f"({result['revolutions']:.2f} revolutions)  \n")
                f.write(f"**Vertices:** {result['vertex_count']}  \n")
                f.write(f"**Calculation time:** {result['calculation_time']:.1f}s  \n")
                f.write(f"**G-code:** `{result['gcode_path']}`  \n")
                f.write(f"**CSV:** `{result['csv_path']}`  \n\n")
            else:
                f.write(f"**Status:** ❌ FAILED  \n")
                f.write(f"**Errors:**  \n")
                for error in result['errors']:
                    f.write(f"- {error}  \n")
                f.write("\n")

    print(f"📝 Markdown report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run BlenderCAM 4-axis validation tests in batch mode"
    )
    parser.add_argument(
        "--strategies",
        type=str,
        default="HELIX,PARALLELR",
        help="Comma-separated list of strategies (default: HELIX,PARALLELR)"
    )
    parser.add_argument(
        "--posts",
        type=str,
        default="GRBL,ISO,EMC,MACH3",
        help="Comma-separated list of post-processors (default: GRBL,ISO,EMC,MACH3)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for results (default: current directory)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate markdown report in addition to JSON"
    )

    args = parser.parse_args()

    strategies = [s.strip().upper() for s in args.strategies.split(',')]
    posts = [p.strip().upper() for p in args.posts.split(',')]

    # Validate inputs
    valid_strategies = ["HELIX", "PARALLEL", "PARALLELR", "CROSS"]
    valid_posts = ["GRBL", "ISO", "EMC", "MACH3"]

    for s in strategies:
        if s not in valid_strategies:
            print(f"ERROR: Invalid strategy '{s}'. Valid: {', '.join(valid_strategies)}")
            sys.exit(1)

    for p in posts:
        if p not in valid_posts:
            print(f"ERROR: Invalid post-processor '{p}'. Valid: {', '.join(valid_posts)}")
            sys.exit(1)

    # Run batch tests
    summary = run_batch_tests(strategies, posts, args.output_dir)

    # Generate markdown report if requested
    if args.report:
        report_path = Path(args.output_dir or Path.cwd()) / \
                     f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        generate_markdown_report(summary, report_path)

    # Exit with error code if any tests failed
    sys.exit(0 if summary['failure_count'] == 0 else 1)


if __name__ == "__main__":
    main()
