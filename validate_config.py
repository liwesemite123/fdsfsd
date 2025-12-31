#!/usr/bin/env python3
"""
Configuration validator for Carrd automation script
Checks that all required files and configurations are in place
"""

import os
from pathlib import Path
import sys


def check_directory(path: str, name: str) -> bool:
    """Check if a directory exists"""
    if Path(path).exists():
        print(f"✓ {name} directory exists: {path}")
        return True
    else:
        print(f"✗ {name} directory missing: {path}")
        return False


def check_file(path: str, name: str, required: bool = True) -> bool:
    """Check if a file exists"""
    if Path(path).exists():
        print(f"✓ {name} file exists: {path}")
        return True
    else:
        if required:
            print(f"✗ {name} file missing: {path}")
        else:
            print(f"⚠ {name} file missing (optional): {path}")
        return not required


def check_file_content(path: str, name: str) -> bool:
    """Check if a file has content"""
    try:
        with open(path, 'r') as f:
            content = f.read().strip()
            # Filter out comments
            lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
            if lines:
                print(f"✓ {name} has content ({len(lines)} lines)")
                return True
            else:
                print(f"⚠ {name} exists but is empty or only has comments")
                return False
    except Exception as e:
        print(f"✗ Error reading {name}: {e}")
        return False


def main():
    """Main validation function"""
    print("=" * 60)
    print("Carrd Automation Configuration Validator")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check directories
    print("Checking directories...")
    all_good &= check_directory("proxy", "Proxy")
    all_good &= check_directory("SITE", "Site configuration")
    print()
    
    # Check required files
    print("Checking required files...")
    all_good &= check_file("carrd_automation.py", "Main script")
    all_good &= check_file("requirements.txt", "Requirements")
    all_good &= check_file("SITE/title.txt", "Site title")
    all_good &= check_file("emails.txt", "Recipient emails")
    all_good &= check_file("proxy/proxies.txt", "Proxy list", required=False)
    print()
    
    # Check file contents
    print("Checking file contents...")
    if Path("SITE/title.txt").exists():
        check_file_content("SITE/title.txt", "Site title")
    
    if Path("emails.txt").exists():
        has_emails = check_file_content("emails.txt", "Recipient emails")
        if not has_emails:
            print("  → Please add recipient emails to emails.txt")
    
    if Path("proxy/proxies.txt").exists():
        has_proxies = check_file_content("proxy/proxies.txt", "Proxy list")
        if not has_proxies:
            print("  → Script will run without proxies")
    print()
    
    # Check Python dependencies
    print("Checking Python dependencies...")
    try:
        import playwright
        print("✓ playwright is installed")
        
        # Check if browsers are installed
        import subprocess
        try:
            result = subprocess.run(
                ['playwright', 'install', '--dry-run', 'chromium'],
                capture_output=True,
                text=True,
                timeout=10
            )
            # If chromium is not installed, the dry-run will indicate it
            if 'chromium' in result.stdout.lower() or result.returncode == 0:
                print("✓ Playwright browsers appear to be installed")
            else:
                print("⚠ Playwright browsers may not be installed")
                print("  → Run: playwright install chromium")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠ Could not verify browser installation")
            print("  → Run: playwright install chromium")
    except ImportError:
        print("✗ playwright is not installed")
        print("  → Run: pip install playwright && playwright install chromium")
        all_good = False
    
    try:
        import loguru
        print("✓ loguru is installed")
    except ImportError:
        print("✗ loguru is not installed")
        print("  → Run: pip install -r requirements.txt")
        all_good = False
    
    try:
        import aiohttp
        print("✓ aiohttp is installed")
    except ImportError:
        print("✗ aiohttp is not installed")
        print("  → Run: pip install -r requirements.txt")
        all_good = False
    print()
    
    # Summary
    print("=" * 60)
    if all_good:
        print("✓ All checks passed! You're ready to run the automation.")
        print()
        print("To run the script:")
        print("  python carrd_automation.py")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print()
        print("Quick setup:")
        print("  1. pip install -r requirements.txt")
        print("  2. playwright install chromium")
        print("  3. Add recipient emails to emails.txt")
        print("  4. (Optional) Add proxies to proxy/proxies.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
