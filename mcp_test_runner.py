#!/usr/bin/env python
"""
MCP Test Runner for SpotifyScraper

This script executes the MCP (Mock, Capture, Playback) tests for the SpotifyScraper
package. It uses VCR.py to record and replay HTTP interactions, allowing for tests
that validate real-world behavior without requiring constant network access.

Usage:
    python mcp_test_runner.py [--record] [--clean]

Options:
    --record    Force recording new cassettes (overwrite existing ones)
    --clean     Delete all existing cassettes before recording
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Path to the VCR cassettes directory
VCR_CASSETTE_DIR = Path(__file__).parent / "tests" / "fixtures" / "vcr_cassettes"


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run MCP tests for SpotifyScraper")
    parser.add_argument(
        "--record",
        action="store_true",
        help="Force recording new cassettes (overwrite existing ones)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete all existing cassettes before recording",
    )
    return parser.parse_args()


def clean_cassettes():
    """Delete all existing VCR cassettes."""
    if VCR_CASSETTE_DIR.exists():
        print(f"Cleaning cassettes directory: {VCR_CASSETTE_DIR}")
        for cassette in VCR_CASSETTE_DIR.glob("*.yaml"):
            print(f"  Deleting {cassette.name}")
            cassette.unlink()
    else:
        print(f"Creating cassettes directory: {VCR_CASSETTE_DIR}")
        VCR_CASSETTE_DIR.mkdir(parents=True, exist_ok=True)


def run_mcp_tests(record=False):
    """Run the MCP tests."""
    # Set environment variable to control VCR recording mode if needed
    env = os.environ.copy()
    if record:
        env["VCR_RECORD_MODE"] = "all"
    
    # Find all MCP test files
    test_dir = Path(__file__).parent / "tests" / "unit"
    mcp_test_files = list(test_dir.glob("*mcp*.py"))
    
    if not mcp_test_files:
        print("No MCP test files found!")
        return False
    
    print(f"Running {len(mcp_test_files)} MCP test files:")
    for test_file in mcp_test_files:
        print(f"  {test_file.name}")
    
    # Run pytest with the MCP test files
    cmd = [sys.executable, "-m", "pytest"] + [str(f) for f in mcp_test_files] + ["-v"]
    print("\nExecuting:", " ".join(cmd))
    
    result = subprocess.run(cmd, env=env)
    return result.returncode == 0


def main():
    """Main entry point."""
    args = parse_args()
    
    if args.clean:
        clean_cassettes()
    
    success = run_mcp_tests(record=args.record)
    
    if success:
        print("\n✅ MCP tests passed successfully!")
        return 0
    else:
        print("\n❌ MCP tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())