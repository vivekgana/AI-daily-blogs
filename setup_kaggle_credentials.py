#!/usr/bin/env python3
"""
Setup Kaggle Credentials Helper

This script helps you set up Kaggle credentials from kaggle.json file.
It will:
1. Read your kaggle.json file
2. Update your .env file with the credentials
3. Test the connection

Usage:
    python setup_kaggle_credentials.py
"""

import os
import sys
import json
from pathlib import Path

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


def find_kaggle_json():
    """Find kaggle.json file."""
    print("🔍 Looking for kaggle.json...\n")

    # Check common locations
    locations = [
        Path.home() / ".kaggle" / "kaggle.json",  # Default location
        Path.cwd() / "kaggle.json",                # Current directory
        Path.home() / "Downloads" / "kaggle.json"  # Downloads folder
    ]

    for location in locations:
        if location.exists():
            print(f"✅ Found kaggle.json at: {location}\n")
            return location

    print("❌ kaggle.json not found in common locations:")
    for location in locations:
        print(f"   - {location}")
    print()
    return None


def read_kaggle_credentials(file_path):
    """Read credentials from kaggle.json."""
    try:
        with open(file_path, 'r') as f:
            creds = json.load(f)

        username = creds.get('username')
        key = creds.get('key')

        if not username or not key:
            print("❌ Invalid kaggle.json format")
            return None, None

        return username, key
    except Exception as e:
        print(f"❌ Error reading kaggle.json: {e}")
        return None, None


def update_env_file(username, key):
    """Update .env file with Kaggle credentials."""
    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        print("❌ .env file not found!")
        return False

    try:
        # Read existing .env
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update credentials
        updated_lines = []
        username_updated = False
        key_updated = False

        for line in lines:
            if line.startswith('KAGGLE_USERNAME='):
                updated_lines.append(f'KAGGLE_USERNAME={username}\n')
                username_updated = True
            elif line.startswith('KAGGLE_KEY='):
                updated_lines.append(f'KAGGLE_KEY={key}\n')
                key_updated = True
            else:
                updated_lines.append(line)

        # Add if not found
        if not username_updated:
            updated_lines.append(f'\nKAGGLE_USERNAME={username}\n')
        if not key_updated:
            updated_lines.append(f'KAGGLE_KEY={key}\n')

        # Write back
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)

        print("✅ Updated .env file with Kaggle credentials\n")
        return True

    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


def test_credentials():
    """Test Kaggle credentials."""
    print("🧪 Testing Kaggle API connection...\n")

    try:
        from dotenv import load_dotenv
        from kaggle.api.kaggle_api_extended import KaggleApi

        # Reload .env
        env_path = Path(__file__).parent / ".env"
        load_dotenv(env_path, override=True)

        api = KaggleApi()
        api.authenticate()

        competitions = api.competitions_list()

        if competitions:
            print(f"✅ Success! Connected to Kaggle API")
            print(f"   Found {len(competitions)} competitions\n")
            print("Sample competitions:")
            for i, comp in enumerate(competitions[:3], 1):
                print(f"   {i}. {comp.title}")
            print()
            return True
        else:
            print("⚠️  Connected but no competitions found")
            return True

    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Kaggle Credentials Setup Helper")
    print("=" * 60)
    print()

    # Step 1: Find kaggle.json
    kaggle_json_path = find_kaggle_json()

    if not kaggle_json_path:
        print("\n📥 Please download kaggle.json:")
        print("   1. Go to: https://www.kaggle.com/settings/account")
        print("   2. Scroll to 'API' section")
        print("   3. Click 'Create New Token'")
        print("   4. Save kaggle.json to one of these locations:")
        print(f"      - {Path.home() / '.kaggle'}")
        print(f"      - {Path.cwd()}")
        print("   5. Run this script again")
        print()
        sys.exit(1)

    # Step 2: Read credentials
    print("📖 Reading credentials from kaggle.json...\n")
    username, key = read_kaggle_credentials(kaggle_json_path)

    if not username or not key:
        print("❌ Failed to read credentials")
        sys.exit(1)

    # Mask the key for display
    masked_key = key[:4] + "*" * (len(key) - 8) + key[-4:]
    print(f"Username: {username}")
    print(f"API Key:  {masked_key}\n")

    # Step 3: Update .env file
    print("💾 Updating .env file...\n")
    if not update_env_file(username, key):
        sys.exit(1)

    # Step 4: Test connection
    if test_credentials():
        print("=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print()
        print("Your Kaggle credentials are now configured and working.")
        print()
        print("Next steps:")
        print("1. Run tests: pytest tests/unit/ -v")
        print("2. Run blog generation: python src/main.py")
        print("3. Update GitHub Secrets with these credentials")
        print()
    else:
        print("=" * 60)
        print("⚠️  Setup Complete But Test Failed")
        print("=" * 60)
        print()
        print("Credentials were updated in .env but the test failed.")
        print("This could be due to:")
        print("  - Network issues")
        print("  - Kaggle API rate limits")
        print("  - Invalid credentials")
        print()
        print("Try running: python test_kaggle_simple.py")
        print()


if __name__ == '__main__':
    main()
