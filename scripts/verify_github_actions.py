#!/usr/bin/env python3
"""
Verify GitHub Actions status and provide setup instructions.
"""

import subprocess
import json
import sys
from typing import Dict, List, Tuple


def run_command(cmd: List[str]) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_secrets() -> Dict[str, bool]:
    """Check which secrets are configured."""
    required_secrets = {
        "PYPI_API_TOKEN": True,
        "ANTHROPIC_API_KEY": True,
        "CODECOV_TOKEN": False,
        "TEST_PYPI_TOKEN": False,
        "DOCKERHUB_USERNAME": False,
        "DOCKERHUB_TOKEN": False,
        "READTHEDOCS_TOKEN": False,
        "SPOTIFY_TEST_TRACK_ID": False,
        "SPOTIFY_TEST_ALBUM_ID": False,
        "SPOTIFY_TEST_ARTIST_ID": False,
        "SPOTIFY_TEST_PLAYLIST_ID": False,
    }
    
    success, output = run_command(["gh", "secret", "list"])
    if not success:
        print("❌ Failed to check secrets. Make sure 'gh' CLI is installed and authenticated.")
        return {}
    
    configured_secrets = set(line.split()[0] for line in output.strip().split('\n') if line)
    
    results = {}
    for secret, is_required in required_secrets.items():
        results[secret] = secret in configured_secrets
    
    return results


def check_workflows() -> Dict[str, str]:
    """Check recent workflow runs."""
    success, output = run_command([
        "gh", "run", "list", "--limit", "10", "--json", 
        "workflowName,status,conclusion,event"
    ])
    
    if not success:
        print("❌ Failed to check workflow runs.")
        return {}
    
    runs = json.loads(output)
    
    # Get latest run for each workflow
    workflows = {}
    for run in runs:
        name = run["workflowName"]
        if name not in workflows:
            if run["status"] == "completed":
                workflows[name] = run["conclusion"]
            else:
                workflows[name] = run["status"]
    
    return workflows


def main():
    """Main verification function."""
    print("🔍 SpotifyScraper GitHub Actions Verification")
    print("=" * 50)
    
    # Check secrets
    print("\n📋 Checking GitHub Secrets...")
    secrets = check_secrets()
    
    if secrets:
        print("\n✅ Required Secrets:")
        for secret, configured in secrets.items():
            if secret in ["PYPI_API_TOKEN", "ANTHROPIC_API_KEY"]:
                status = "✅" if configured else "❌"
                print(f"  {status} {secret}")
        
        print("\n📦 Optional Secrets (for extended features):")
        for secret, configured in secrets.items():
            if secret not in ["PYPI_API_TOKEN", "ANTHROPIC_API_KEY"]:
                status = "✅" if configured else "⚠️"
                print(f"  {status} {secret}")
    
    # Check workflows
    print("\n🔄 Checking Workflow Status...")
    workflows = check_workflows()
    
    if workflows:
        all_passing = True
        for name, status in workflows.items():
            if status == "success":
                print(f"  ✅ {name}")
            elif status in ["queued", "in_progress"]:
                print(f"  🔄 {name} ({status})")
            elif status == "skipped":
                print(f"  ⏭️  {name} (skipped)")
            else:
                print(f"  ❌ {name} ({status})")
                all_passing = False
        
        if all_passing:
            print("\n✅ All workflows are passing!")
        else:
            print("\n⚠️  Some workflows need attention.")
    
    # Instructions for missing secrets
    missing_optional = [s for s, c in secrets.items() 
                       if not c and s not in ["PYPI_API_TOKEN", "ANTHROPIC_API_KEY"]]
    
    if missing_optional:
        print("\n📝 To add optional secrets for full functionality:")
        print("   1. Go to: https://github.com/AliAkhtari78/SpotifyScraper/settings/secrets/actions")
        print("   2. Click 'New repository secret'")
        print("   3. Refer to GITHUB_SECRETS_SETUP.md for detailed instructions")
        print(f"\n   Missing optional secrets: {', '.join(missing_optional)}")
    
    print("\n✨ Verification complete!")
    
    # Return appropriate exit code
    required_ok = all(secrets.get(s, False) for s in ["PYPI_API_TOKEN", "ANTHROPIC_API_KEY"])
    if not required_ok:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()