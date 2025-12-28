#!/usr/bin/env python3
"""Test script to diagnose Kaggle leaderboard issues."""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_kaggle_connection():
    """Test basic Kaggle API connection."""
    print("\n" + "=" * 80)
    print("KAGGLE API CONNECTION TEST")
    print("=" * 80)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        print("[PASS] Kaggle API imported successfully")

        # Check for credentials
        kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
        if os.path.exists(kaggle_json):
            print(f"[PASS] Kaggle credentials found at {kaggle_json}")
        else:
            print(f"[FAIL] Kaggle credentials not found at {kaggle_json}")
            print("       Set KAGGLE_USERNAME and KAGGLE_KEY environment variables")
            return False

        # Authenticate
        api = KaggleApi()
        api.authenticate()
        print("[PASS] Kaggle API authenticated successfully")

        return api

    except ImportError as e:
        print(f"[FAIL] Failed to import Kaggle API: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Authentication failed: {type(e).__name__}: {e}")
        return False


def test_list_competitions(api):
    """Test listing competitions."""
    print("\n" + "=" * 80)
    print("COMPETITION LISTING TEST")
    print("=" * 80)

    try:
        print("[INFO] Fetching competitions...")
        competitions = api.competitions_list()

        if not competitions:
            print("[WARN] No competitions returned")
            return []

        print(f"[PASS] Found {len(competitions)} competitions")

        # Show first 3 competitions
        print("\nFirst 3 competitions:")
        for i, comp in enumerate(competitions[:3]):
            print(f"\n  {i+1}. {comp.title}")
            print(f"     ID: {comp.id}")
            print(f"     URL: {comp.url}")
            print(f"     Teams: {comp.teamCount}")
            print(f"     Reward: {comp.reward}")

        return competitions[:3]

    except Exception as e:
        print(f"[FAIL] Error listing competitions: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_leaderboard_methods(api, competition_id):
    """Test different leaderboard retrieval methods."""
    print("\n" + "=" * 80)
    print(f"LEADERBOARD TEST: {competition_id}")
    print("=" * 80)

    # Method 1: competition_leaderboard_view
    print("\n[Method 1] Testing competition_leaderboard_view()...")
    try:
        leaderboard = api.competition_leaderboard_view(competition_id)
        print(f"[INFO] Returned type: {type(leaderboard)}")

        if leaderboard:
            print(f"[INFO] Leaderboard length: {len(leaderboard)}")

            # Inspect first entry
            if len(leaderboard) > 0:
                first_entry = leaderboard[0]
                print(f"[INFO] First entry type: {type(first_entry)}")
                print(f"[INFO] First entry attributes: {dir(first_entry)}")

                # Try to access common attributes
                attrs_to_check = ['teamId', 'teamName', 'score', 'rank',
                                 'submissionDate', 'entries']
                print("\n[INFO] Checking attributes:")
                for attr in attrs_to_check:
                    if hasattr(first_entry, attr):
                        value = getattr(first_entry, attr)
                        print(f"  - {attr}: {value} (type: {type(value)})")

                print("\n[PASS] Method 1 returned data")
                return True
            else:
                print("[WARN] Method 1 returned empty leaderboard")
                return False
        else:
            print("[WARN] Method 1 returned None")
            return False

    except Exception as e:
        print(f"[FAIL] Method 1 error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_leaderboard_download(api, competition_id):
    """Test leaderboard download method."""
    print("\n[Method 2] Testing competition_leaderboard_download()...")
    try:
        result = api.competition_leaderboard_download(competition_id, path='.')
        print(f"[INFO] Download result: {result}")

        # Check if file was created
        leaderboard_file = f"{competition_id}.zip"
        if os.path.exists(leaderboard_file):
            print(f"[PASS] Leaderboard file downloaded: {leaderboard_file}")
            # Clean up
            os.remove(leaderboard_file)
            return True
        else:
            print("[WARN] No leaderboard file created")
            return False

    except Exception as e:
        print(f"[FAIL] Method 2 error: {type(e).__name__}: {e}")
        return False


def test_kaggle_collector():
    """Test the KaggleCollector class."""
    print("\n" + "=" * 80)
    print("KAGGLE COLLECTOR CLASS TEST")
    print("=" * 80)

    try:
        from src.collectors.kaggle_collector import KaggleCollector
        from src.utils.config_loader import ConfigLoader

        config = ConfigLoader()
        collector = KaggleCollector(config)

        print("[PASS] KaggleCollector initialized")

        # Get competitions
        print("\n[INFO] Getting active competitions...")
        comps = collector.get_active_competitions()
        print(f"[PASS] Found {len(comps)} competitions")

        if comps:
            test_comp = comps[0]
            comp_id = test_comp['id']
            print(f"\n[INFO] Testing leaderboard for: {test_comp['title']}")
            print(f"       Competition ID: {comp_id}")

            # Try to get leaderboard
            leaderboard = collector.get_competition_leaderboard(comp_id)

            if leaderboard is not None and not leaderboard.empty:
                print(f"[PASS] Leaderboard retrieved: {len(leaderboard)} entries")
                print("\nFirst 5 entries:")
                print(leaderboard.head())
                return True
            else:
                print("[WARN] Leaderboard returned None or empty")
                print("       This is expected for private/unavailable leaderboards")
                return None
        else:
            print("[FAIL] No competitions found")
            return False

    except Exception as e:
        print(f"[FAIL] Collector test error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\nKAGGLE LEADERBOARD DIAGNOSTIC TESTS")
    print("=" * 80)

    # Test 1: Connection
    api = test_kaggle_connection()
    if not api:
        print("\n[FAIL] Cannot proceed without API connection")
        return 1

    # Test 2: List competitions
    competitions = test_list_competitions(api)
    if not competitions:
        print("\n[FAIL] Cannot proceed without competitions")
        return 1

    # Test 3: Test leaderboard methods on first competition
    comp_id = competitions[0].id
    print(f"\n[INFO] Using competition: {competitions[0].title} (ID: {comp_id})")

    leaderboard_works = test_leaderboard_methods(api, comp_id)

    # Test 4: Try download method
    # test_leaderboard_download(api, comp_id)

    # Test 5: Test collector class
    print("\n")
    collector_works = test_kaggle_collector()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    print(f"API Connection: PASS")
    print(f"Competition Listing: PASS")
    print(f"Leaderboard Access: {'PASS' if leaderboard_works else 'WARN/FAIL'}")
    print(f"Collector Class: {'PASS' if collector_works else 'WARN/FAIL'}")

    if leaderboard_works and collector_works:
        print("\n[RESULT] All tests passed")
        return 0
    elif collector_works is None:
        print("\n[RESULT] Tests completed - leaderboard may be unavailable for test competition")
        return 0
    else:
        print("\n[RESULT] Some tests failed - check errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
