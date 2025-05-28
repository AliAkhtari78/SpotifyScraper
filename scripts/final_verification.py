#!/usr/bin/env python3
"""
Final Comprehensive Verification for SpotifyScraper v2.0.19
Ensures the package is 100% production-ready with full automation
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

# Add src to path for development testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import spotify_scraper
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import create_browser
from spotify_scraper.core.config import Config
from spotify_scraper.utils.url import validate_url, extract_id


class FinalVerification:
    """Comprehensive verification of SpotifyScraper functionality."""
    
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.version = spotify_scraper.__version__
    
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        if passed:
            self.results["passed"].append(test_name)
            print(f"✅ {test_name}")
        else:
            self.results["failed"].append((test_name, message))
            print(f"❌ {test_name}: {message}")
    
    def test_version(self):
        """Test version consistency."""
        print("\n🔍 Testing Version Consistency...")
        
        # Check __init__.py version
        init_version = spotify_scraper.__version__
        
        # Check pyproject.toml version
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, 'r') as f:
            for line in f:
                if line.strip().startswith('version = '):
                    pyproject_version = line.split('"')[1]
                    break
        
        if init_version == pyproject_version:
            self.log_result("Version consistency", True)
        else:
            self.log_result(
                "Version consistency", 
                False, 
                f"Mismatch: __init__.py={init_version}, pyproject.toml={pyproject_version}"
            )
    
    def test_imports(self):
        """Test all imports work correctly."""
        print("\n🔍 Testing Imports...")
        
        imports = [
            ("Client", "from spotify_scraper import SpotifyClient"),
            ("Config", "from spotify_scraper import Config"),
            ("Exceptions", "from spotify_scraper.core.exceptions import SpotifyScraperError"),
            ("Browsers", "from spotify_scraper.browsers import create_browser"),
            ("Extractors", "from spotify_scraper.extractors import TrackExtractor"),
            ("Utils", "from spotify_scraper.utils.url import validate_url"),
            ("CLI", "from spotify_scraper.cli import cli"),
        ]
        
        for name, import_stmt in imports:
            try:
                exec(import_stmt)
                self.log_result(f"Import {name}", True)
            except ImportError as e:
                self.log_result(f"Import {name}", False, str(e))
    
    def test_client_creation(self):
        """Test client creation with various configurations."""
        print("\n🔍 Testing Client Creation...")
        
        # Default client
        try:
            client = SpotifyClient()
            self.log_result("Default client creation", True)
            client.close()
        except Exception as e:
            self.log_result("Default client creation", False, str(e))
        
        # Client with browser type
        try:
            client = SpotifyClient(browser_type="requests")
            self.log_result("Client with browser type", True)
            client.close()
        except Exception as e:
            self.log_result("Client with browser type", False, str(e))
    
    def test_browser_creation(self):
        """Test browser creation."""
        print("\n🔍 Testing Browser Creation...")
        
        try:
            browser = create_browser("requests")
            self.log_result("RequestsBrowser creation", True)
        except Exception as e:
            self.log_result("RequestsBrowser creation", False, str(e))
    
    def test_url_utilities(self):
        """Test URL utility functions."""
        print("\n🔍 Testing URL Utilities...")
        
        test_urls = [
            ("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6", "track", "6rqhFgbbKwnb9MLmUQDhG6"),
            ("https://open.spotify.com/album/1A2GTWGtFfWp7KSQTwWOyo", "album", "1A2GTWGtFfWp7KSQTwWOyo"),
            ("https://open.spotify.com/artist/0YC192cP3KPCRWx8zr8MfZ", "artist", "0YC192cP3KPCRWx8zr8MfZ"),
            ("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M", "playlist", "37i9dQZF1DXcBWIGoYBM5M"),
        ]
        
        for url, expected_type, expected_id in test_urls:
            try:
                # Test URL validation
                validate_url(url)
                
                # Test ID extraction
                extracted_id = extract_id(url)
                if extracted_id == expected_id:
                    self.log_result(f"URL utilities for {expected_type}", True)
                else:
                    self.log_result(
                        f"URL utilities for {expected_type}", 
                        False, 
                        f"Expected ID {expected_id}, got {extracted_id}"
                    )
            except Exception as e:
                self.log_result(f"URL utilities for {expected_type}", False, str(e))
    
    def test_configuration(self):
        """Test configuration system."""
        print("\n🔍 Testing Configuration...")
        
        try:
            config = Config()
            config_dict = config.as_dict()
            
            # Check essential config keys
            essential_keys = ["timeout", "cache_enabled", "browser_type"]
            missing_keys = [k for k in essential_keys if k not in config_dict]
            
            if not missing_keys:
                self.log_result("Configuration system", True)
            else:
                self.log_result(
                    "Configuration system", 
                    False, 
                    f"Missing keys: {missing_keys}"
                )
        except Exception as e:
            self.log_result("Configuration system", False, str(e))
    
    def test_cli_availability(self):
        """Test CLI command availability."""
        print("\n🔍 Testing CLI...")
        
        try:
            from spotify_scraper.cli import cli
            commands = list(cli.commands.keys())
            expected_commands = ["track", "album", "artist", "playlist", "download"]
            
            missing_commands = [c for c in expected_commands if c not in commands]
            
            if not missing_commands:
                self.log_result("CLI commands", True)
            else:
                self.log_result(
                    "CLI commands", 
                    False, 
                    f"Missing commands: {missing_commands}"
                )
        except Exception as e:
            self.log_result("CLI commands", False, str(e))
    
    def test_dependencies(self):
        """Test all dependencies are available."""
        print("\n🔍 Testing Dependencies...")
        
        required_modules = [
            ("requests", "requests"),
            ("beautifulsoup4", "bs4"),
            ("lxml", "lxml"),
            ("click", "click"),
            ("rich", "rich"),
            ("pyyaml", "yaml"),
            ("eyeD3", "eyed3"),
            ("tqdm", "tqdm"),
        ]
        
        for package_name, import_name in required_modules:
            try:
                __import__(import_name)
                self.log_result(f"Dependency {package_name}", True)
            except ImportError:
                self.log_result(f"Dependency {package_name}", False, "Not installed")
    
    def test_pypi_package(self):
        """Test if package can be installed from PyPI."""
        print("\n🔍 Testing PyPI Package...")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a virtual environment
            venv_path = Path(tmpdir) / "test_venv"
            try:
                subprocess.run(
                    [sys.executable, "-m", "venv", str(venv_path)],
                    check=True,
                    capture_output=True
                )
                
                # Install from PyPI
                pip_path = venv_path / ("Scripts" if os.name == "nt" else "bin") / "pip"
                result = subprocess.run(
                    [str(pip_path), "install", "--no-cache-dir", "spotifyscraper"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.log_result("PyPI installation", True)
                else:
                    self.log_result("PyPI installation", False, result.stderr)
                    
            except Exception as e:
                self.log_result("PyPI installation", False, str(e))
    
    def generate_report(self):
        """Generate final report."""
        print("\n" + "="*60)
        print("📊 Final Verification Report")
        print("="*60)
        print(f"📦 Package: SpotifyScraper v{self.version}")
        print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_tests = len(self.results["passed"]) + len(self.results["failed"])
        pass_rate = (len(self.results["passed"]) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Results: {len(self.results['passed'])}/{total_tests} passed ({pass_rate:.1f}%)")
        
        if self.results["failed"]:
            print(f"\n❌ Failed Tests ({len(self.results['failed'])}):")
            for test, message in self.results["failed"]:
                print(f"  • {test}: {message}")
        
        if self.results["warnings"]:
            print(f"\n⚠️  Warnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"  • {warning}")
        
        if pass_rate == 100:
            print("\n✅ Package is 100% production-ready!")
        elif pass_rate >= 90:
            print("\n🟡 Package is mostly ready, minor issues to fix")
        else:
            print("\n🔴 Package has critical issues that need fixing")
        
        print("\n" + "="*60)
        
        return pass_rate == 100
    
    def run_all_tests(self):
        """Run all verification tests."""
        print(f"🧪 Final Verification for SpotifyScraper v{self.version}")
        print("="*60)
        
        self.test_version()
        self.test_imports()
        self.test_client_creation()
        self.test_browser_creation()
        self.test_url_utilities()
        self.test_configuration()
        self.test_cli_availability()
        self.test_dependencies()
        self.test_pypi_package()
        
        return self.generate_report()


def main():
    """Main entry point."""
    verifier = FinalVerification()
    success = verifier.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()