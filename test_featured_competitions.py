#!/usr/bin/env python3
"""
Test Featured competition filtering and daily submission statistics.
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

def test_featured_filtering():
    """Test Featured competition filtering and daily submission logic."""
    print("=" * 60)
    print("Featured Competitions & Daily Submission Test")
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
        print("Test 1: Fetching all competitions (no filter)")
        print("-" * 60)
        all_comps = collector.get_active_competitions(filter_featured=False)
        print(f"✅ Found {len(all_comps)} total competitions")
        print()

        # Test 2: Get Featured competitions only
        print("-" * 60)
        print("Test 2: Fetching Featured competitions only")
        print("-" * 60)
        featured_comps = collector.get_active_competitions(filter_featured=True)
        print(f"✅ Found {len(featured_comps)} Featured competitions")

        if featured_comps:
            print("\nFeatured Competitions:")
            for i, comp in enumerate(featured_comps[:10], 1):
                print(f"\n{i}. {comp['title']}")
                print(f"   ID: {comp['id']}")
                print(f"   Category: {comp.get('category', 'N/A')}")
                print(f"   Prize: {comp.get('reward', 'N/A')}")
                print(f"   Teams: {comp.get('teamCount', 0)}")
                print(f"   Max Daily Submissions: {comp.get('maxDailySubmissions', 'N/A')}")
        else:
            print("\n⚠️  No Featured competitions found in current active competitions")
            print("   This might indicate all competitions are 'Getting Started' or 'Playground'")
            print()

        # Test 3: Get daily submission statistics
        if featured_comps:
            print()
            print("-" * 60)
            print("Test 3: Daily Submission Statistics")
            print("-" * 60)

            test_comp = featured_comps[0]
            print(f"Testing with: {test_comp['title']}")
            print(f"Competition ID: {test_comp['id']}")
            print()

            # Get submission statistics
            stats = collector.get_daily_submission_stats(test_comp['id'])

            print("Submission Statistics:")
            print(f"  Max Daily Submissions: {stats['max_daily_submissions'] or 'Unlimited/Unknown'}")
            print(f"  Unique Submitters: {stats['unique_submitters']}")
            print(f"  Total Submissions: {stats['total_submissions']}")
            print(f"  Avg Submissions/Team: {stats['avg_submissions_per_team']:.2f}" if stats['avg_submissions_per_team'] > 0 else "  Avg Submissions/Team: N/A")
            print()

            # Test 4: Get algorithms if no leaderboard
            print("-" * 60)
            print("Test 4: Algorithm Extraction (fallback)")
            print("-" * 60)

            leaderboard = collector.get_competition_leaderboard(test_comp['id'])

            if leaderboard is None or leaderboard.empty:
                print("ℹ️  Leaderboard not available - extracting algorithms from kernels...")
                algorithms = collector.get_algorithms_from_submissions(test_comp['id'], max_kernels=20)

                if algorithms:
                    print(f"✅ Detected {len(algorithms)} algorithms:")
                    for i, algo in enumerate(algorithms[:10], 1):
                        print(f"   {i}. {algo}")
                else:
                    print("ℹ️  No algorithms detected from kernel titles")
            else:
                print(f"✅ Leaderboard available with {len(leaderboard)} entries")
                print("   (Algorithm extraction not needed)")

        print()
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Total competitions: {len(all_comps)}")
        print(f"Featured competitions: {len(featured_comps)}")

        if all_comps:
            filter_rate = len(featured_comps) / len(all_comps) * 100
            print(f"Filter rate: {filter_rate:.1f}% are Featured competitions")

        # Show category breakdown
        if all_comps:
            print("\nCategory Breakdown:")
            categories = {}
            for comp in all_comps:
                cat = comp.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1

            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}")

        print()
        print("✅ All tests completed successfully!")

        return True

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = test_featured_filtering()
    sys.exit(0 if success else 1)
