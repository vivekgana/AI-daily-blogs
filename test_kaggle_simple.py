#!/usr/bin/env python3
"""
Minimal Kaggle Authentication Test

Quick test to verify Kaggle credentials work.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print("✅ Loaded credentials from .env file\n")


def test_kaggle():
    """Test Kaggle authentication."""
    print("🔍 Testing Kaggle Authentication...\n")

    # Check credentials
    username = os.getenv('KAGGLE_USERNAME')
    key = os.getenv('KAGGLE_KEY')

    if not username or not key:
        print("❌ Credentials not set!")
        print("\nSet them first:")
        print("  Windows: $env:KAGGLE_USERNAME = 'your_username'")
        print("           $env:KAGGLE_KEY = 'your_api_key'")
        print("  Linux:   export KAGGLE_USERNAME='your_username'")
        print("           export KAGGLE_KEY='your_api_key'")
        return

    print(f"Username: {username}")
    print(f"API Key: {key[:4]}...{key[-4:]}\n")

    # Test API
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()

        competitions = api.competitions_list()

        print(f"✅ Success! Found {len(competitions)} competitions\n")

        # Show top 3
        print("Top 3 competitions:")
        for i, comp in enumerate(competitions[:3], 1):
            print(f"  {i}. {comp.title}")

        print("\n✅ Authentication working!")
        print("\nYou can now update GitHub Secrets with these credentials.")

    except Exception as e:
        print(f"❌ Failed: {e}")
        print("\nPossible issues:")
        print("  - Invalid credentials")
        print("  - Network problem")
        print("  - Rate limit exceeded")


if __name__ == '__main__':
    test_kaggle()
