#!/usr/bin/env python3
"""
Test AGI/ASI filtering and algorithm extraction from Kaggle competitions.
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

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config_loader import ConfigLoader
from src.collectors.kaggle_collector import KaggleCollector

def test_agi_filtering():
    """Test AGI/ASI competition filtering."""
    print("=" * 60)
    print("AGI/ASI Filtering and Algorithm Extraction Test")
    print("=" * 60)
    print()

    try:
        # Load configuration
        config = ConfigLoader()
        print("✅ Configuration loaded")

        # Initialize Kaggle collector
        collector = KaggleCollector(config)
        print("✅ Kaggle collector initialized")
        print()

        # Test 1: Get all competitions (no filtering)
        print("-" * 60)
        print("Test 1: Fetching all competitions (no AGI filter)")
        print("-" * 60)
        all_comps = collector.get_active_competitions(filter_agi=False)
        print(f"✅ Found {len(all_comps)} total competitions")
        print()

        # Test 2: Get AGI/ASI filtered competitions
        print("-" * 60)
        print("Test 2: Fetching AGI/ASI competitions only")
        print("-" * 60)
        agi_comps = collector.get_active_competitions(filter_agi=True)
        print(f"✅ Found {len(agi_comps)} AGI/ASI competitions")

        if agi_comps:
            print("\nAGI/ASI Competitions:")
            for i, comp in enumerate(agi_comps[:5], 1):
                print(f"{i}. {comp['title']}")
                print(f"   ID: {comp['id']}")
                print(f"   Prize: {comp.get('reward', 'N/A')}")
                print(f"   Teams: {comp.get('teamCount', 0)}")
                print()
        else:
            print("\n⚠️  No AGI/ASI competitions found in current active competitions")
            print("   This might be normal if there are no AGI-related competitions active")
            print()

        # Test 3: Extract algorithms from a competition
        if agi_comps:
            print("-" * 60)
            print("Test 3: Extracting algorithms from submissions")
            print("-" * 60)

            test_comp = agi_comps[0]
            print(f"Testing with: {test_comp['title']}")
            print(f"Competition ID: {test_comp['id']}")
            print()

            # Try to get leaderboard first
            leaderboard = collector.get_competition_leaderboard(test_comp['id'])

            if leaderboard is not None and not leaderboard.empty:
                print(f"✅ Leaderboard available: {len(leaderboard)} entries")
            else:
                print("ℹ️  Leaderboard not available (private or unavailable)")
                print("   Attempting to extract algorithms from kernels...")
                print()

                # Extract algorithms from submissions
                algorithms = collector.get_algorithms_from_submissions(test_comp['id'], max_kernels=20)

                if algorithms:
                    print(f"✅ Detected {len(algorithms)} algorithms:")
                    for i, algo in enumerate(algorithms, 1):
                        print(f"   {i}. {algo}")
                else:
                    print("ℹ️  No algorithms detected from kernel titles")
                    print("   This might be normal for new competitions with few submissions")

        print()
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Total competitions: {len(all_comps)}")
        print(f"AGI/ASI competitions: {len(agi_comps)}")
        print(f"Filter rate: {len(agi_comps)/len(all_comps)*100:.1f}% matched AGI/ASI criteria" if all_comps else "N/A")
        print()
        print("✅ All tests completed successfully!")

        return True

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = test_agi_filtering()
    sys.exit(0 if success else 1)
