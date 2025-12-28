#!/usr/bin/env python3
"""
Test API connectivity using GitHub Secrets.

This script uses GitHub CLI to verify that secrets are configured,
then tests API connections using environment variables set by the user.

Requirements:
- GitHub CLI (gh) installed and authenticated
- Environment variables set with actual secret values
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def run_command(cmd, capture_output=True, timeout=30):
    """Run shell command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_github_cli():
    """Check if GitHub CLI is available."""
    print("\nChecking GitHub CLI...")

    returncode, stdout, stderr = run_command("gh --version")
    if returncode != 0:
        print("[ERROR] GitHub CLI not installed")
        print("        Install from: https://cli.github.com/")
        return False

    version = stdout.split('\n')[0]
    print(f"[SUCCESS] {version}")

    # Check authentication
    returncode, stdout, stderr = run_command("gh auth status")
    if returncode != 0:
        print("[ERROR] GitHub CLI not authenticated")
        print("        Run: gh auth login")
        return False

    print("[SUCCESS] GitHub CLI authenticated")
    return True


def list_github_secrets():
    """List configured GitHub Secrets."""
    print_header("STEP 1: Verify GitHub Secrets Configuration")

    print("\nFetching secrets from GitHub repository...")

    cmd = 'gh secret list --repo vivekgana/AI-daily-blogs --json name,updatedAt'
    returncode, stdout, stderr = run_command(cmd)

    if returncode != 0:
        print(f"[ERROR] Failed to fetch secrets: {stderr}")
        return False

    try:
        secrets = json.loads(stdout)

        required_secrets = {
            'KAGGLE_USERNAME': False,
            'KAGGLE_PASSWORD': False,
            'GEMINI_API_KEY': False,
            'MY_GITHUB_ACTION': False
        }

        print("\nGitHub Secrets Status:")
        print("-" * 70)

        for secret in secrets:
            name = secret['name']
            updated = secret.get('updatedAt', 'Unknown')

            if name in required_secrets:
                required_secrets[name] = True
                print(f"[FOUND] {name}")
                print(f"        Last updated: {updated}")
            else:
                print(f"[INFO]  {name} (not required for this test)")

        print("-" * 70)

        # Check required secrets
        all_configured = True
        for secret_name, found in required_secrets.items():
            if not found:
                if secret_name == 'MY_GITHUB_ACTION':
                    print(f"[WARNING] {secret_name}: Not found (optional for API tests)")
                else:
                    print(f"[ERROR] {secret_name}: Not found")
                    all_configured = False

        if all_configured:
            print("\n[SUCCESS] All required secrets are configured in GitHub!")
        else:
            print("\n[ERROR] Some required secrets are missing")
            print("\nConfigure secrets at:")
            print("https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions")

        return all_configured

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse secrets: {e}")
        return False


def test_environment_variables():
    """Test that environment variables are set locally."""
    print_header("STEP 2: Check Local Environment Variables")

    print("\nNote: GitHub CLI cannot retrieve secret VALUES for security.")
    print("You must set environment variables manually with your actual credentials.")
    print("")

    credentials = {
        'KAGGLE_USERNAME': os.getenv('KAGGLE_USERNAME'),
        'KAGGLE_PASSWORD': os.getenv('KAGGLE_PASSWORD') or os.getenv('KAGGLE_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN') or os.getenv('MY_GITHUB_ACTION')
    }

    all_set = True
    for name, value in credentials.items():
        if value and len(value) > 10 and not value.startswith('your_'):
            print(f"[SUCCESS] {name}: Set (length: {len(value)})")
        else:
            if name == 'GITHUB_TOKEN':
                print(f"[WARNING] {name}: Not set (optional)")
            else:
                print(f"[ERROR] {name}: Not set or invalid")
                all_set = False

    if not all_set:
        print("\n[ERROR] Required environment variables not set")
        print("\nSet them using PowerShell:")
        print('  $env:KAGGLE_USERNAME = "your_username"')
        print('  $env:KAGGLE_PASSWORD = "your_api_key"')
        print('  $env:GEMINI_API_KEY = "your_gemini_key"')
        print("\nOr run: .\\set_github_secrets_env.ps1")
        return False

    print("\n[SUCCESS] All required environment variables are set!")
    return True


def test_kaggle_api():
    """Test Kaggle API connection."""
    print_header("STEP 3: Test Kaggle API Connection")

    try:
        print("\nTesting Kaggle API...")

        # Set up Kaggle credentials
        kaggle_username = os.getenv('KAGGLE_USERNAME')
        kaggle_key = os.getenv('KAGGLE_PASSWORD') or os.getenv('KAGGLE_KEY')

        if not kaggle_username or not kaggle_key:
            print("[ERROR] Kaggle credentials not in environment")
            return False

        # Create kaggle.json temporarily
        kaggle_dir = Path.home() / '.kaggle'
        kaggle_dir.mkdir(exist_ok=True)
        kaggle_json = kaggle_dir / 'kaggle.json'

        with open(kaggle_json, 'w') as f:
            json.dump({
                'username': kaggle_username,
                'key': kaggle_key
            }, f)

        # Set permissions (Unix only)
        if sys.platform != 'win32':
            os.chmod(kaggle_json, 0o600)

        print(f"[INFO] Kaggle credentials written to {kaggle_json}")

        # Test API
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()

        print("[SUCCESS] Kaggle API authenticated")

        # Try to list competitions
        competitions = api.competitions_list()
        print(f"[SUCCESS] Retrieved {len(competitions)} competitions")

        # Show first 3 competitions
        print("\nSample competitions:")
        for i, comp in enumerate(competitions[:3]):
            print(f"  {i+1}. {comp.title}")
            print(f"     Teams: {comp.teamCount}, Reward: {comp.reward}")

        return True

    except Exception as e:
        print(f"[ERROR] Kaggle API test failed: {type(e).__name__}: {e}")

        if '401' in str(e) or 'Unauthorized' in str(e):
            print("\n[FIX] Invalid Kaggle credentials")
            print("      1. Go to https://www.kaggle.com/settings/account")
            print("      2. Click 'Create New Token'")
            print("      3. Download kaggle.json")
            print("      4. Set environment variables:")
            print('         $env:KAGGLE_USERNAME = "username_from_json"')
            print('         $env:KAGGLE_PASSWORD = "key_from_json"')

        return False


def test_gemini_api():
    """Test Gemini API connection."""
    print_header("STEP 4: Test Gemini API Connection")

    try:
        print("\nTesting Gemini API...")

        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            print("[ERROR] GEMINI_API_KEY not in environment")
            return False

        import google.generativeai as genai
        genai.configure(api_key=gemini_key)

        print("[SUCCESS] Gemini API configured")

        # Test with simple prompt
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content("Say 'API connection successful!'")

        if hasattr(response, 'text') and response.text:
            print("[SUCCESS] Gemini API response received")
            print(f"[INFO] Response: {response.text[:100]}...")
            return True
        else:
            print("[ERROR] No response from Gemini API")
            return False

    except Exception as e:
        print(f"[ERROR] Gemini API test failed: {type(e).__name__}: {e}")

        if 'API_KEY_INVALID' in str(e) or 'invalid' in str(e).lower():
            print("\n[FIX] Invalid Gemini API key")
            print("      1. Go to https://makersuite.google.com/app/apikey")
            print("      2. Create new API key")
            print("      3. Set environment variable:")
            print('         $env:GEMINI_API_KEY = "your_api_key"')

        return False


def test_github_api():
    """Test GitHub API connection (optional)."""
    print_header("STEP 5: Test GitHub API Connection (Optional)")

    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('MY_GITHUB_ACTION')

    if not github_token:
        print("\n[SKIP] GitHub token not configured (optional)")
        return True

    try:
        print("\nTesting GitHub API...")

        from github import Github
        gh = Github(github_token)

        # Test authentication
        user = gh.get_user()
        print(f"[SUCCESS] GitHub API authenticated")
        print(f"[INFO] Logged in as: {user.login}")

        # Test repository access
        repo = gh.get_repo("vivekgana/AI-daily-blogs")
        print(f"[SUCCESS] Repository access: {repo.full_name}")
        print(f"[INFO] Stars: {repo.stargazers_count}, Forks: {repo.forks_count}")

        return True

    except Exception as e:
        print(f"[WARNING] GitHub API test failed: {type(e).__name__}: {e}")
        print("[INFO] GitHub API is optional for blog generation")
        return True  # Not critical


def main():
    """Main test function."""
    print("=" * 70)
    print(" TEST API CONNECTIVITY USING GITHUB SECRETS")
    print("=" * 70)

    # Check GitHub CLI
    gh_available = check_github_cli()

    if gh_available:
        # List GitHub Secrets
        secrets_ok = list_github_secrets()
        if not secrets_ok:
            print("\n[WARNING] Some secrets not configured in GitHub")
            print("          Tests will use local environment variables")
    else:
        print("\n[WARNING] GitHub CLI not available")
        print("          Will test using local environment variables only")

    # Test environment variables
    if not test_environment_variables():
        print("\n[ABORT] Cannot proceed without environment variables")
        return 1

    # Test each API
    results = []

    # Kaggle
    kaggle_ok = test_kaggle_api()
    results.append(("Kaggle API", kaggle_ok))

    # Gemini
    gemini_ok = test_gemini_api()
    results.append(("Gemini API", gemini_ok))

    # GitHub (optional)
    github_ok = test_github_api()
    results.append(("GitHub API", github_ok))

    # Summary
    print_header("SUMMARY")

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")

    passed_count = sum(1 for _, p in results if p)
    total_required = 2  # Kaggle and Gemini are required

    if passed_count >= total_required:
        print("\n[SUCCESS] All required API connections working!")
        print("\nYou can now run:")
        print("  python test_blog_generation_local.py")
        print("\nOr run the full blog generation:")
        print("  python src/main.py")
        return 0
    else:
        print("\n[ERROR] Some required API connections failed")
        print("\nFix the errors above and try again")
        return 1


if __name__ == '__main__':
    sys.exit(main())
