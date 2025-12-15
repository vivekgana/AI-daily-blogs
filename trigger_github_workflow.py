#!/usr/bin/env python3
"""Trigger GitHub Actions workflow locally.

This script triggers the test-on-demand workflow via GitHub API,
bypassing SSL certificate verification issues.
"""
import os
import sys
import requests
from datetime import datetime

def trigger_workflow(test_suite='credentials', verbose=False):
    """Trigger GitHub Actions workflow via API."""

    # Get GitHub token
    github_token = os.getenv('MY_GITHUB_ACTION')
    if not github_token:
        print("ERROR: MY_GITHUB_ACTION environment variable not set")
        print("\nSet it with:")
        print("  Windows CMD: set MY_GITHUB_ACTION=your_token_here")
        print("  PowerShell:  $env:MY_GITHUB_ACTION=\"your_token_here\"")
        return False

    print("=" * 70)
    print(f" TRIGGERING GITHUB ACTIONS WORKFLOW")
    print("=" * 70)
    print(f"Repository: vivekgana/AI-daily-blogs")
    print(f"Workflow: test-on-demand.yml")
    print(f"Branch: fix/gemini-api-and-kaggle-leaderboard")
    print(f"Test Suite: {test_suite}")
    print(f"Verbose: {verbose}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # API endpoint
    url = "https://api.github.com/repos/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml/dispatches"

    # Request headers
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Request body
    data = {
        "ref": "fix/gemini-api-and-kaggle-leaderboard",
        "inputs": {
            "test_suite": test_suite,
            "verbose": str(verbose).lower()
        }
    }

    try:
        print("\nSending request to GitHub API...")

        # Make request with SSL verification disabled for local testing
        response = requests.post(
            url,
            headers=headers,
            json=data,
            verify=False,  # Disable SSL verification
            timeout=30
        )

        # Check response
        if response.status_code == 204:
            print("\n✅ SUCCESS! Workflow triggered successfully!")
            print("\nView workflow run:")
            print("  https://github.com/vivekgana/AI-daily-blogs/actions")
            print("\nThe workflow will start in a few seconds.")
            print("Refresh the Actions page to see it running.")
            return True

        elif response.status_code == 401:
            print("\n❌ ERROR: Authentication failed (401)")
            print("\nPossible issues:")
            print("  1. MY_GITHUB_ACTION token is invalid or expired")
            print("  2. Token doesn't have 'repo' or 'workflow' scope")
            print("\nFix:")
            print("  1. Go to: https://github.com/settings/tokens")
            print("  2. Generate new token (classic)")
            print("  3. Select scopes: 'repo' and 'workflow'")
            print("  4. Update MY_GITHUB_ACTION environment variable")
            return False

        elif response.status_code == 404:
            print("\n❌ ERROR: Workflow not found (404)")
            print("\nPossible issues:")
            print("  1. Workflow file doesn't exist on the branch")
            print("  2. Repository name is incorrect")
            print("  3. Branch name is incorrect")
            return False

        elif response.status_code == 422:
            print("\n❌ ERROR: Validation failed (422)")
            print("\nPossible issues:")
            print("  1. Branch doesn't exist")
            print("  2. Invalid input parameters")
            print(f"\nResponse: {response.text}")
            return False

        else:
            print(f"\n❌ ERROR: Unexpected response ({response.status_code})")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.SSLError as e:
        print(f"\n❌ ERROR: SSL Certificate verification failed")
        print(f"Details: {e}")
        print("\nThis script disables SSL verification, but there may be a deeper issue.")
        return False

    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out")
        print("Check your internet connection and try again.")
        return False

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ERROR: Connection failed")
        print(f"Details: {e}")
        print("Check your internet connection.")
        return False

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""

    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print("\n" + "=" * 70)
    print(" GITHUB ACTIONS WORKFLOW TRIGGER")
    print("=" * 70)

    # Check if token is set
    if not os.getenv('MY_GITHUB_ACTION'):
        print("\nERROR: MY_GITHUB_ACTION environment variable not set!")
        print("\nTo set it:")
        print("\nWindows Command Prompt:")
        print("  set MY_GITHUB_ACTION=your_github_token_here")
        print("  python trigger_github_workflow.py")
        print("\nWindows PowerShell:")
        print("  $env:MY_GITHUB_ACTION=\"your_github_token_here\"")
        print("  python trigger_github_workflow.py")
        print("\nGet token from: https://github.com/settings/tokens")
        print("Required scopes: 'repo' and 'workflow'")
        return 1

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Trigger GitHub Actions workflow')
    parser.add_argument(
        '--test-suite',
        choices=['all', 'unit', 'integration', 'kaggle', 'github', 'research', 'credentials'],
        default='credentials',
        help='Test suite to run (default: credentials)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Trigger workflow
    success = trigger_workflow(args.test_suite, args.verbose)

    if success:
        print("\n" + "=" * 70)
        print(" NEXT STEPS")
        print("=" * 70)
        print("\n1. Go to: https://github.com/vivekgana/AI-daily-blogs/actions")
        print("2. Look for the latest workflow run (top of the list)")
        print("3. Click on it to see results")
        print("4. Wait for it to complete (30 seconds - 5 minutes)")
        print("\nExpected results:")
        print("  credentials: All 4 secrets configured ✅")
        print("  all: 40+ tests passing ✅")
        return 0
    else:
        print("\n" + "=" * 70)
        print(" TROUBLESHOOTING")
        print("=" * 70)
        print("\nIf authentication failed:")
        print("  1. Verify token is correct")
        print("  2. Check token has 'repo' and 'workflow' scopes")
        print("  3. Try generating a new token")
        print("\nAlternative: Use GitHub web interface")
        print("  https://github.com/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml")
        return 1

if __name__ == '__main__':
    sys.exit(main())
