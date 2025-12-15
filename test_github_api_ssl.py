#!/usr/bin/env python3
"""Simple test to verify Python requests library works with SSL bypass."""
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("Testing GitHub API connection with SSL bypass...")

try:
    # Test simple API call
    response = requests.get(
        "https://api.github.com/repos/vivekgana/AI-daily-blogs",
        verify=False,  # Bypass SSL verification
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        print("[SUCCESS] Connected to GitHub API")
        print(f"   Repository: {data['full_name']}")
        print(f"   Description: {data.get('description', 'N/A')}")
        print(f"   Default Branch: {data['default_branch']}")
        print("\n[SUCCESS] SSL bypass is working correctly!")
        print("\nYou can now use the trigger script:")
        print("  1. Set token: set MY_GITHUB_ACTION=your_token_here")
        print("  2. Run: python trigger_github_workflow.py --test-suite credentials")
    else:
        print(f"[ERROR] Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"[ERROR] {e}")
    print("\nTroubleshooting:")
    print("  - Check internet connection")
    print("  - Check if corporate proxy is blocking")
