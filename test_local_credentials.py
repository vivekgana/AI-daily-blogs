#!/usr/bin/env python3
"""Quick test script to verify local credentials setup.

This script validates that all API credentials are properly configured
for local development and testing.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_env_file():
    """Test if .env file exists and can be loaded."""
    print("\n" + "=" * 70)
    print("TEST 1: Environment File Check")
    print("=" * 70)

    # Check if .env exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"[PASS] .env file found")
    else:
        print(f"[WARN] .env file not found")
        print(f"       Create it from .env.example:")
        print(f"       cp .env.example .env")
        return False

    # Try to load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[PASS] python-dotenv loaded successfully")
        return True
    except ImportError:
        print("[FAIL] python-dotenv not installed")
        print("       Install it: pip install python-dotenv")
        return False

def test_gemini_credentials():
    """Test Gemini API credentials."""
    print("\n" + "=" * 70)
    print("TEST 2: Gemini API Credentials")
    print("=" * 70)

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("[FAIL] GEMINI_API_KEY not found in environment")
        print("       Add it to your .env file:")
        print("       GEMINI_API_KEY=your_key_here")
        return False

    print(f"[PASS] GEMINI_API_KEY found")
    print(f"       Length: {len(api_key)} characters")
    print(f"       Preview: {api_key[:15]}...{api_key[-5:]}")

    # Test API connection
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        # Try to list models
        models = list(genai.list_models())
        print(f"[PASS] Gemini API connection successful")
        print(f"       Found {len(models)} available models")

        # Test content generation
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content("Say 'Hello!'")

        if hasattr(response, 'text') and response.text:
            print(f"[PASS] Content generation successful")
            print(f"       Response: {response.text[:50]}...")
            return True
        else:
            print(f"[WARN] No text in response")
            return False

    except Exception as e:
        print(f"[FAIL] Gemini API error: {type(e).__name__}: {e}")
        return False

def test_kaggle_credentials():
    """Test Kaggle API credentials."""
    print("\n" + "=" * 70)
    print("TEST 3: Kaggle API Credentials")
    print("=" * 70)

    from dotenv import load_dotenv
    load_dotenv()

    # Check for credentials
    username = os.getenv('KAGGLE_USERNAME')
    key = os.getenv('KAGGLE_KEY')

    # Check kaggle.json
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    has_json = os.path.exists(kaggle_json)

    if username and key:
        print(f"[PASS] Kaggle credentials found in .env")
        print(f"       Username: {username}")
        print(f"       Key: {key[:10]}...{key[-5:] if len(key) > 15 else ''}")

        # Set them for Kaggle API
        os.environ['KAGGLE_USERNAME'] = username
        os.environ['KAGGLE_KEY'] = key

    elif has_json:
        print(f"[PASS] kaggle.json found at {kaggle_json}")
    else:
        print(f"[FAIL] No Kaggle credentials found")
        print(f"       Option 1: Add to .env file:")
        print(f"         KAGGLE_USERNAME=your_username")
        print(f"         KAGGLE_KEY=your_api_key")
        print(f"       Option 2: Place kaggle.json at {kaggle_json}")
        return False

    # Test API connection
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        print(f"[PASS] Kaggle API authenticated")

        # Test listing competitions
        competitions = api.competitions_list()
        print(f"[PASS] Kaggle API connection successful")
        print(f"       Found {len(competitions)} competitions")

        if competitions:
            print(f"       First: {competitions[0].title}")

        return True

    except Exception as e:
        print(f"[FAIL] Kaggle API error: {type(e).__name__}: {e}")
        return False

def test_github_credentials():
    """Test GitHub API credentials."""
    print("\n" + "=" * 70)
    print("TEST 4: GitHub API Credentials")
    print("=" * 70)

    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv('GITHUB_TOKEN')

    if not token:
        print(f"[WARN] GITHUB_TOKEN not found (optional for public repos)")
        print(f"       Get token from: https://github.com/settings/tokens")
        print(f"       Note: Tests may still work but with rate limits")
        return None

    print(f"[PASS] GITHUB_TOKEN found")
    print(f"       Length: {len(token)} characters")
    print(f"       Preview: {token[:10]}...{token[-5:]}")

    # Test API connection
    try:
        from github import Github

        gh = Github(token)
        user = gh.get_user()

        print(f"[PASS] GitHub API connection successful")
        print(f"       User: {user.login}")
        print(f"       API rate limit: {gh.get_rate_limit().core.remaining}/{gh.get_rate_limit().core.limit}")

        # Test search
        repos = gh.search_repositories('xgboost language:python', sort='stars')
        first_repo = list(repos)[:1]

        if first_repo:
            print(f"[PASS] Repository search successful")
            print(f"       Found: {first_repo[0].full_name}")
            return True
        else:
            print(f"[WARN] Search returned no results")
            return False

    except ImportError:
        print(f"[FAIL] PyGithub not installed")
        print(f"       Install it: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"[FAIL] GitHub API error: {type(e).__name__}: {e}")
        return False


def test_email_credentials():
    """Test email credentials (optional)."""
    print("\n" + "=" * 70)
    print("TEST 5: Email Credentials (Optional)")
    print("=" * 70)

    from dotenv import load_dotenv
    load_dotenv()

    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    to = os.getenv('EMAIL_TO')

    if username and password and to:
        print(f"[PASS] Email credentials found")
        print(f"       From: {username}")
        print(f"       To: {to}")
        print(f"       Password length: {len(password)} characters")
        return True
    else:
        print(f"[SKIP] Email credentials not configured (optional)")
        return None

def main():
    """Run all credential tests."""
    print("\n" + "=" * 70)
    print(" LOCAL CREDENTIALS TEST")
    print("=" * 70)

    results = []

    # Test 1: .env file
    if test_env_file():
        # Test 2: Gemini
        results.append(("Gemini API", test_gemini_credentials()))

        # Test 3: Kaggle
        results.append(("Kaggle API", test_kaggle_credentials()))

        # Test 4: GitHub
        github_result = test_github_credentials()
        if github_result is not None:
            results.append(("GitHub API", github_result))

        # Test 5: Email (optional)
        email_result = test_email_credentials()
        if email_result is not None:
            results.append(("Email", email_result))
    else:
        print("\n[FAIL] Cannot proceed without .env file or python-dotenv")
        return 1

    # Summary
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)

    for name, passed in results:
        if passed:
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\nResult: {passed_count}/{total} tests passed")

    if passed_count == total:
        print("\n*** All credentials configured correctly!")
        print("    You can now run:")
        print("    - pytest tests/unit/ -v")
        print("    - pytest tests/integration/test_collectors_integration.py -v")
        print("    - python src/main.py")
        return 0
    else:
        print("\n*** Some credentials need configuration")
        print("    See docs/LOCAL-SETUP-GUIDE.md for help")
        return 1

if __name__ == '__main__':
    sys.exit(main())
