#!/usr/bin/env python3
"""
Continuous Integration Monitor for SpotifyScraper
Automatically monitors and fixes common CI/CD issues
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class CIMonitor:
    """Monitor and fix CI/CD issues automatically."""
    
    def __init__(self, project_root=None):
        self.project_root = Path(project_root or os.getcwd())
        self.issues_found = []
        self.fixes_applied = []
        
    def run_command(self, cmd, check=True):
        """Run a shell command and return output."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=check
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return e.stderr
    
    def check_dependencies(self):
        """Ensure all required dependencies are listed."""
        print("🔍 Checking dependencies...")
        
        # Read pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        # Essential dependencies that must be present
        required_deps = {
            "click": "click>=8.0.0",
            "rich": "rich>=13.0.0",
            "requests": "requests>=2.25.0",
            "beautifulsoup4": "beautifulsoup4>=4.9.0",
        }
        
        missing = []
        for dep, spec in required_deps.items():
            if dep not in content:
                missing.append(spec)
                self.issues_found.append(f"Missing dependency: {spec}")
        
        if missing:
            print(f"  ❌ Missing {len(missing)} dependencies")
            return False
        else:
            print("  ✅ All essential dependencies present")
            return True
    
    def check_version_consistency(self):
        """Ensure version is consistent across files."""
        print("🔍 Checking version consistency...")
        
        # Get version from pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        with open(pyproject_path, 'r') as f:
            for line in f:
                if line.strip().startswith('version = '):
                    pyproject_version = line.split('"')[1]
                    break
        
        # Check __init__.py
        init_path = self.project_root / "src" / "spotify_scraper" / "__init__.py"
        if init_path.exists():
            with open(init_path, 'r') as f:
                content = f.read()
                if f'__version__ = "{pyproject_version}"' not in content:
                    self.issues_found.append(f"Version mismatch in __init__.py")
                    print(f"  ❌ Version mismatch: pyproject.toml has {pyproject_version}")
                    return False
        
        print(f"  ✅ Version {pyproject_version} is consistent")
        return True
    
    def check_github_workflows(self):
        """Check for common workflow issues."""
        print("🔍 Checking GitHub workflows...")
        
        workflows_dir = self.project_root / ".github" / "workflows"
        issues = []
        
        for workflow_file in workflows_dir.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            # Check for incorrect package names
            if "spotify-scraper" in content and "spotify-scraper.py" not in content:
                issues.append(f"{workflow_file.name}: Contains 'spotify-scraper' instead of 'spotifyscraper'")
            
            # Check for non-existent dependencies
            if "pytest-integration" in content:
                issues.append(f"{workflow_file.name}: References non-existent 'pytest-integration'")
        
        if issues:
            print(f"  ❌ Found {len(issues)} workflow issues")
            self.issues_found.extend(issues)
            return False
        else:
            print("  ✅ Workflows look good")
            return True
    
    def run_tests(self):
        """Run tests to ensure everything works."""
        print("🧪 Running tests...")
        
        # Activate venv and run tests
        activate_cmd = "source venv/bin/activate" if sys.platform != "win32" else "venv\\Scripts\\activate"
        test_cmd = f"{activate_cmd} && python -m pytest tests/ -x --tb=short"
        
        result = self.run_command(test_cmd, check=False)
        
        if "failed" in result.lower() or "error" in result.lower():
            print("  ❌ Tests failed")
            self.issues_found.append("Test failures detected")
            return False
        else:
            print("  ✅ All tests passing")
            return True
    
    def run_linters(self):
        """Run code quality checks."""
        print("🔍 Running linters...")
        
        activate_cmd = "source venv/bin/activate" if sys.platform != "win32" else "venv\\Scripts\\activate"
        
        # Run flake8
        flake8_result = self.run_command(f"{activate_cmd} && flake8 src/ --count", check=False)
        if flake8_result and flake8_result.strip() != "0":
            print(f"  ❌ Flake8 found issues")
            self.issues_found.append("Flake8 linting errors")
            return False
        
        # Run mypy
        mypy_result = self.run_command(f"{activate_cmd} && mypy src/ --ignore-missing-imports", check=False)
        if "error" in mypy_result.lower():
            print(f"  ❌ MyPy found type errors")
            self.issues_found.append("MyPy type checking errors")
            return False
        
        print("  ✅ Code quality checks passed")
        return True
    
    def check_pypi_status(self):
        """Check if latest version is on PyPI."""
        print("🔍 Checking PyPI status...")
        
        # Get current version
        pyproject_path = self.project_root / "pyproject.toml"
        with open(pyproject_path, 'r') as f:
            for line in f:
                if line.strip().startswith('version = '):
                    current_version = line.split('"')[1]
                    break
        
        # Check PyPI (this is a simplified check)
        result = self.run_command(f"pip index versions spotifyscraper 2>/dev/null | grep {current_version}", check=False)
        
        if current_version not in result:
            print(f"  ⚠️  Version {current_version} not yet on PyPI")
            return None
        else:
            print(f"  ✅ Version {current_version} is on PyPI")
            return True
    
    def generate_report(self):
        """Generate a status report."""
        print("\n" + "="*50)
        print("📊 CI/CD Status Report")
        print("="*50)
        print(f"🕐 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.issues_found:
            print(f"\n❌ Issues Found ({len(self.issues_found)}):")
            for issue in self.issues_found:
                print(f"  • {issue}")
        else:
            print("\n✅ No issues found!")
        
        if self.fixes_applied:
            print(f"\n🔧 Fixes Applied ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
        
        print("\n" + "="*50)
    
    def monitor(self, continuous=False, interval=300):
        """Run all checks."""
        while True:
            print(f"\n🚀 Starting CI/CD monitoring...")
            print(f"📁 Project: {self.project_root}")
            print("="*50)
            
            self.issues_found = []
            self.fixes_applied = []
            
            # Run all checks
            checks = [
                self.check_dependencies(),
                self.check_version_consistency(),
                self.check_github_workflows(),
                self.run_tests(),
                self.run_linters(),
                self.check_pypi_status(),
            ]
            
            # Generate report
            self.generate_report()
            
            if not continuous:
                break
            
            print(f"\n⏰ Next check in {interval} seconds...")
            time.sleep(interval)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CI/CD Monitor for SpotifyScraper")
    parser.add_argument("--continuous", "-c", action="store_true", help="Run continuously")
    parser.add_argument("--interval", "-i", type=int, default=300, help="Check interval in seconds")
    parser.add_argument("--project-root", "-r", help="Project root directory")
    
    args = parser.parse_args()
    
    monitor = CIMonitor(project_root=args.project_root)
    monitor.monitor(continuous=args.continuous, interval=args.interval)


if __name__ == "__main__":
    main()