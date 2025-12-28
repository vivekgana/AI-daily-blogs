#!/usr/bin/env python3
"""
Test API Connectivity for all services.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

def test_kaggle_api():
    """Test Kaggle API connectivity."""
    print("\n" + "="*60)
    print("Testing Kaggle API")
    print("="*60)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        print("✅ Authentication successful")

        # Test competitions list
        print("\nFetching competitions...")
        competitions = api.competitions_list()
        print(f"✅ Found {len(competitions)} competitions")

        # Test leaderboard (using a real competition)
        if competitions:
            comp_id = competitions[0].ref
            print(f"\nTesting leaderboard for: {comp_id}")
            try:
                leaderboard = api.competition_leaderboard_view(comp_id)
                if leaderboard:
                    print(f"✅ Leaderboard retrieved: {len(leaderboard)} entries")
                else:
                    print("ℹ️  No leaderboard available (may be private)")
            except Exception as e:
                print(f"⚠️  Leaderboard error: {type(e).__name__}: {e}")

        return True

    except Exception as e:
        print(f"❌ Kaggle API Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_gemini_api():
    """Test Gemini API connectivity."""
    print("\n" + "="*60)
    print("Testing Gemini API")
    print("="*60)

    try:
        import google.generativeai as genai

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return False

        genai.configure(api_key=api_key)
        print("✅ API configured")

        # Test model
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Model initialized")

        # Test generation
        response = model.generate_content("Say 'API test successful'")
        print(f"✅ Generation successful: {response.text}")

        return True

    except Exception as e:
        print(f"❌ Gemini API Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_github_api():
    """Test GitHub API connectivity."""
    print("\n" + "="*60)
    print("Testing GitHub API")
    print("="*60)

    try:
        import requests

        token = os.getenv('GITHUB_TOKEN')
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
            print("✅ Using authenticated requests")
        else:
            print("ℹ️  No token - using unauthenticated requests")

        # Test GitHub API
        response = requests.get(
            'https://api.github.com/search/repositories?q=machine+learning&sort=stars&per_page=1',
            headers=headers,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API working: {data['total_count']} repositories found")
            return True
        elif response.status_code == 301:
            print(f"⚠️  301 Redirect Error")
            print(f"   URL: {response.url}")
            print(f"   Redirected to: {response.headers.get('Location', 'Unknown')}")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ GitHub API Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Run all API tests."""
    print("\n" + "="*60)
    print("API Connectivity Test Suite")
    print("="*60)

    results = {
        'Kaggle': test_kaggle_api(),
        'Gemini': test_gemini_api(),
        'GitHub': test_github_api()
    }

    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)

    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}: {'PASS' if status else 'FAIL'}")

    all_pass = all(results.values())
    print("\n" + "="*60)
    if all_pass:
        print("✅ All APIs working correctly!")
    else:
        print("⚠️  Some APIs have issues - see details above")
    print("="*60)

    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
