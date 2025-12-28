#!/usr/bin/env python3
"""
Simple Kaggle Authentication Test Script

This script tests if Kaggle API credentials are configured correctly.
Run this before updating GitHub Secrets to verify your credentials work.

Usage:
    python test_kaggle_auth.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_kaggle_credentials():
    """Test Kaggle API authentication."""
    print("=" * 60)
    print("Kaggle Authentication Test")
    print("=" * 60)
    print()

    # Step 1: Check environment variables
    print("Step 1: Checking environment variables...")
    kaggle_username = os.getenv('KAGGLE_USERNAME')
    kaggle_key = os.getenv('KAGGLE_KEY')

    if not kaggle_username:
        print("❌ KAGGLE_USERNAME not set")
        print("   Set it with: export KAGGLE_USERNAME='your_username'")
        return False
    else:
        print(f"✅ KAGGLE_USERNAME: {kaggle_username}")

    if not kaggle_key:
        print("❌ KAGGLE_KEY not set")
        print("   Set it with: export KAGGLE_KEY='your_api_key'")
        return False
    else:
        # Mask the key for security
        masked_key = kaggle_key[:4] + "*" * (len(kaggle_key) - 8) + kaggle_key[-4:]
        print(f"✅ KAGGLE_KEY: {masked_key}")

    print()

    # Step 2: Check kaggle.json file
    print("Step 2: Checking kaggle.json file...")
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'

    if kaggle_json.exists():
        print(f"✅ Found kaggle.json at: {kaggle_json}")

        # Check file permissions (Unix-like systems)
        if sys.platform != 'win32':
            import stat
            mode = oct(os.stat(kaggle_json).st_mode)[-3:]
            print(f"   File permissions: {mode}")
            if mode != '600':
                print(f"   ⚠️  Warning: Permissions should be 600, currently {mode}")
    else:
        print(f"⚠️  kaggle.json not found at: {kaggle_json}")
        print(f"   Creating it now...")

        # Create the directory if it doesn't exist
        kaggle_dir.mkdir(parents=True, exist_ok=True)

        # Create kaggle.json
        import json
        credentials = {
            "username": kaggle_username,
            "key": kaggle_key
        }

        with open(kaggle_json, 'w') as f:
            json.dump(credentials, f)

        # Set permissions (Unix-like systems)
        if sys.platform != 'win32':
            os.chmod(kaggle_json, 0o600)

        print(f"✅ Created kaggle.json at: {kaggle_json}")

    print()

    # Step 3: Test Kaggle API connection
    print("Step 3: Testing Kaggle API connection...")

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        print("   Initializing Kaggle API...")
        api = KaggleApi()

        print("   Authenticating...")
        api.authenticate()

        print("✅ Authentication successful!")
        print()

        # Step 4: Test API call
        print("Step 4: Testing API call (fetching competitions)...")
        competitions = api.competitions_list()

        if competitions:
            print(f"✅ Successfully fetched {len(competitions)} competitions")
            print()
            print("   Sample competitions:")
            for i, comp in enumerate(competitions[:3], 1):
                print(f"   {i}. {comp.title}")
                print(f"      Category: {comp.category}")
                print(f"      Reward: {comp.reward}")
                print()

            return True
        else:
            print("⚠️  No competitions found (unusual but not necessarily an error)")
            return True

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print()
        print("Common issues:")
        print("  1. Invalid credentials - check your kaggle.json")
        print("  2. Network issues - check your internet connection")
        print("  3. Kaggle API rate limit - wait a few minutes and try again")
        print()
        return False


def print_setup_instructions():
    """Print instructions for setting up Kaggle credentials."""
    print()
    print("=" * 60)
    print("Setup Instructions")
    print("=" * 60)
    print()
    print("1. Get your Kaggle API credentials:")
    print("   - Go to: https://www.kaggle.com/settings/account")
    print("   - Scroll to 'API' section")
    print("   - Click 'Create New Token'")
    print("   - Download kaggle.json")
    print()
    print("2. Set environment variables:")
    print()
    print("   Windows (PowerShell):")
    print("   $env:KAGGLE_USERNAME = 'your_username'")
    print("   $env:KAGGLE_KEY = 'your_api_key'")
    print()
    print("   Linux/macOS (Bash):")
    print("   export KAGGLE_USERNAME='your_username'")
    print("   export KAGGLE_KEY='your_api_key'")
    print()
    print("3. Or place kaggle.json in:")
    print(f"   {Path.home() / '.kaggle' / 'kaggle.json'}")
    print()
    print("4. Run this script again:")
    print("   python test_kaggle_auth.py")
    print()


def main():
    """Main entry point."""
    # Check if credentials are set
    if not os.getenv('KAGGLE_USERNAME') and not os.getenv('KAGGLE_KEY'):
        kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'

        if not kaggle_json.exists():
            print("❌ Kaggle credentials not found!")
            print()
            print("No environment variables set and no kaggle.json found.")
            print_setup_instructions()
            sys.exit(1)
        else:
            # Load from kaggle.json
            import json
            with open(kaggle_json) as f:
                creds = json.load(f)
            os.environ['KAGGLE_USERNAME'] = creds.get('username', '')
            os.environ['KAGGLE_KEY'] = creds.get('key', '')

    # Run the test
    success = test_kaggle_credentials()

    if success:
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print()
        print("Your Kaggle credentials are working correctly.")
        print()
        print("Next steps:")
        print("1. Update GitHub Secrets with these credentials:")
        print("   - KAGGLE_USERNAME")
        print("   - KAGGLE_PASSWORD (use the API key)")
        print()
        print("2. Go to:")
        print("   https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions")
        print()
        print("3. Update the secrets and re-run the workflow")
        print()
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ Test failed!")
        print("=" * 60)
        print()
        print("Please fix the issues above and try again.")
        print_setup_instructions()
        sys.exit(1)


if __name__ == '__main__':
    main()
