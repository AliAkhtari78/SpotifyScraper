#!/usr/bin/env python3
"""
GitHub Actions Monitor and Auto-Fixer for SpotifyScraper
Monitors workflow runs and automatically fixes common issues
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GitHubActionsMonitor:
    """Monitor and fix GitHub Actions issues automatically."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root or os.getcwd())
        self.workflows_dir = self.project_root / ".github" / "workflows"
        self.issues_found = []
        self.fixes_applied = []
        
    def run_command(self, cmd: str, check: bool = True) -> str:
        """Run shell command and return output."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=check
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e.stderr
    
    def get_workflow_runs(self, limit: int = 10) -> List[Dict]:
        """Get recent workflow runs."""
        cmd = f"cd {self.project_root} && gh run list --limit {limit} --json name,status,conclusion,workflowName,createdAt"
        output = self.run_command(cmd, check=False)
        
        if not output or "error" in output.lower():
            print("⚠️  Failed to fetch workflow runs (GitHub API issue)")
            return []
        
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []
    
    def analyze_failures(self, runs: List[Dict]) -> Dict[str, List[str]]:
        """Analyze workflow failures and categorize them."""
        failures = {}
        
        for run in runs:
            if run.get("conclusion") == "failure":
                workflow = run.get("workflowName", "Unknown")
                if workflow not in failures:
                    failures[workflow] = []
                failures[workflow].append(run.get("name", "Unknown job"))
        
        return failures
    
    def check_common_issues(self) -> List[Tuple[str, str, str]]:
        """Check for common workflow issues."""
        issues = []
        
        for workflow_file in self.workflows_dir.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for common issues
            for i, line in enumerate(lines, 1):
                # Wrong package name
                if re.search(r'spotify-scraper(?!\.)', line) and 'spotify-scraper.py' not in line:
                    issues.append((
                        workflow_file.name,
                        f"Line {i}: 'spotify-scraper' should be 'spotifyscraper'",
                        "package_name"
                    ))
                
                # Missing continue-on-error for optional steps
                if 'secrets.' in line and 'if:' not in lines[max(0, i-3):i]:
                    issues.append((
                        workflow_file.name,
                        f"Line {i}: Secret usage without conditional check",
                        "secret_check"
                    ))
                
                # Deprecated actions
                if 'actions/checkout@v2' in line or 'actions/checkout@v3' in line:
                    issues.append((
                        workflow_file.name,
                        f"Line {i}: Using deprecated checkout action version",
                        "deprecated_action"
                    ))
                
                # Non-existent dependencies
                if 'pytest-integration' in line:
                    issues.append((
                        workflow_file.name,
                        f"Line {i}: Non-existent dependency 'pytest-integration'",
                        "bad_dependency"
                    ))
        
        return issues
    
    def auto_fix_issues(self, issues: List[Tuple[str, str, str]]) -> int:
        """Automatically fix detected issues."""
        fixes_count = 0
        
        for workflow, issue, issue_type in issues:
            workflow_path = self.workflows_dir / workflow
            
            with open(workflow_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            if issue_type == "package_name":
                # Fix package name
                content = re.sub(r'spotify-scraper(?!\.py)', 'spotifyscraper', content)
            
            elif issue_type == "deprecated_action":
                # Update to latest action versions
                content = content.replace('actions/checkout@v2', 'actions/checkout@v4')
                content = content.replace('actions/checkout@v3', 'actions/checkout@v4')
                content = content.replace('actions/setup-python@v2', 'actions/setup-python@v5')
                content = content.replace('actions/setup-python@v3', 'actions/setup-python@v5')
                content = content.replace('actions/setup-python@v4', 'actions/setup-python@v5')
            
            elif issue_type == "bad_dependency":
                # Remove bad dependencies
                lines = content.splitlines()
                new_lines = []
                for line in lines:
                    if 'pytest-integration' not in line:
                        new_lines.append(line)
                content = '\n'.join(new_lines)
            
            if content != original_content:
                with open(workflow_path, 'w') as f:
                    f.write(content)
                fixes_count += 1
                self.fixes_applied.append(f"Fixed {issue_type} in {workflow}")
        
        return fixes_count
    
    def check_dependencies(self) -> bool:
        """Verify all required dependencies are properly specified."""
        pyproject_path = self.project_root / "pyproject.toml"
        
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        required_deps = [
            "click",
            "rich",
            "pytest-asyncio",  # Often missing
        ]
        
        missing = []
        for dep in required_deps:
            if f'"{dep}' not in content:
                missing.append(dep)
        
        if missing:
            self.issues_found.extend([f"Missing dependency: {dep}" for dep in missing])
            return False
        
        return True
    
    def check_pytest_config(self) -> bool:
        """Check pytest configuration for common issues."""
        pytest_ini = self.project_root / "pytest.ini"
        
        if not pytest_ini.exists():
            self.issues_found.append("pytest.ini not found")
            return False
        
        with open(pytest_ini, 'r') as f:
            content = f.read()
        
        # Check for common issues
        if 'asyncio_default_fixture_loop_scope = function.0' in content:
            self.issues_found.append("Invalid asyncio configuration in pytest.ini")
            # Auto-fix
            content = content.replace('function.0', 'function')
            with open(pytest_ini, 'w') as f:
                f.write(content)
            self.fixes_applied.append("Fixed asyncio configuration in pytest.ini")
        
        return True
    
    def generate_status_report(self, failures: Dict[str, List[str]]) -> None:
        """Generate a comprehensive status report."""
        print("\n" + "="*60)
        print("📊 GitHub Actions Status Report")
        print("="*60)
        print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if failures:
            print(f"\n❌ Failed Workflows ({len(failures)}):")
            for workflow, jobs in failures.items():
                print(f"\n  📋 {workflow}:")
                for job in set(jobs):  # Remove duplicates
                    print(f"     • {job}")
        else:
            print("\n✅ All workflows passing!")
        
        if self.issues_found:
            print(f"\n⚠️  Issues Found ({len(self.issues_found)}):")
            for issue in self.issues_found:
                print(f"  • {issue}")
        
        if self.fixes_applied:
            print(f"\n🔧 Fixes Applied ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
        
        print("\n" + "="*60)
    
    def suggest_fixes(self, failures: Dict[str, List[str]]) -> None:
        """Suggest fixes for common failure patterns."""
        suggestions = []
        
        for workflow, jobs in failures.items():
            jobs_str = ' '.join(jobs).lower()
            
            if 'docker' in workflow.lower():
                if 'login' in jobs_str or 'push' in jobs_str:
                    suggestions.append(
                        "Docker workflow: Add DOCKERHUB_USERNAME and DOCKERHUB_TOKEN secrets"
                    )
            
            elif 'ci' in workflow.lower():
                if 'pytest' in jobs_str or 'test' in jobs_str:
                    suggestions.append(
                        "CI workflow: Check if pytest-asyncio is installed, verify pytest.ini configuration"
                    )
                if 'codecov' in jobs_str:
                    suggestions.append(
                        "CI workflow: Verify CODECOV_TOKEN secret is set"
                    )
            
            elif 'pages' in workflow.lower():
                suggestions.append(
                    "Pages workflow: This is often a GitHub infrastructure issue, wait and retry"
                )
        
        if suggestions:
            print("\n💡 Suggested Fixes:")
            for suggestion in set(suggestions):
                print(f"  • {suggestion}")
    
    def monitor(self, continuous: bool = False, interval: int = 300) -> None:
        """Run the monitoring process."""
        while True:
            print(f"\n🚀 GitHub Actions Monitor")
            print(f"📁 Repository: {self.project_root}")
            
            self.issues_found = []
            self.fixes_applied = []
            
            # Get recent workflow runs
            runs = self.get_workflow_runs()
            failures = self.analyze_failures(runs)
            
            # Check for common issues
            issues = self.check_common_issues()
            if issues:
                self.issues_found.extend([f"{w}: {i}" for w, i, _ in issues])
                
                # Auto-fix issues
                fixes = self.auto_fix_issues(issues)
                if fixes > 0:
                    print(f"\n🔧 Applied {fixes} automatic fixes")
            
            # Check other configurations
            self.check_dependencies()
            self.check_pytest_config()
            
            # Generate report
            self.generate_status_report(failures)
            
            # Suggest fixes
            if failures:
                self.suggest_fixes(failures)
            
            if not continuous:
                break
            
            print(f"\n⏰ Next check in {interval} seconds...")
            time.sleep(interval)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GitHub Actions Monitor for SpotifyScraper"
    )
    parser.add_argument(
        "--continuous", "-c",
        action="store_true",
        help="Run continuously"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300)"
    )
    parser.add_argument(
        "--fix", "-f",
        action="store_true",
        help="Automatically fix issues"
    )
    
    args = parser.parse_args()
    
    monitor = GitHubActionsMonitor()
    monitor.monitor(continuous=args.continuous, interval=args.interval)


if __name__ == "__main__":
    main()