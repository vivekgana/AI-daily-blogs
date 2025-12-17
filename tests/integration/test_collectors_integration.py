"""Integration tests for all data collectors.

This module tests real API connections to:
- Kaggle API
- GitHub API
- arXiv API (Research)
- Gemini AI

These tests work with both:
- Local development: Reads from .env file
- GitHub Actions: Reads from GitHub Secrets
"""
import unittest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env file (local development)
# In GitHub Actions, secrets are already in environment
try:
    from dotenv import load_dotenv
    load_dotenv()  # This will be no-op if variables already set
except ImportError:
    pass  # dotenv not required in CI/CD

from src.collectors.kaggle_collector import KaggleCollector
from src.collectors.github_collector import GitHubCollector
from src.collectors.research_collector import ResearchCollector
from src.utils.config_loader import ConfigLoader


class TestKaggleCollectorIntegration(unittest.TestCase):
    """Integration tests for Kaggle collector."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        # Check for credentials
        cls.has_credentials = bool(
            os.getenv('KAGGLE_USERNAME') and os.getenv('KAGGLE_KEY')
        ) or os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json'))

        if not cls.has_credentials:
            print("\n⚠️  SKIPPING Kaggle tests: No credentials found")
            print("   Add KAGGLE_USERNAME and KAGGLE_KEY to .env file")
            return

        cls.config = ConfigLoader()
        cls.collector = KaggleCollector(cls.config)

    def setUp(self):
        """Check if we should skip tests."""
        if not self.has_credentials:
            self.skipTest("Kaggle credentials not configured")

    def test_01_get_active_competitions(self):
        """Test fetching active competitions."""
        print("\n[TEST] Fetching active competitions from Kaggle...")

        competitions = self.collector.get_active_competitions()

        # Assertions
        self.assertIsNotNone(competitions, "Should return competitions list")
        self.assertIsInstance(competitions, list, "Should return a list")
        self.assertGreater(len(competitions), 0, "Should have at least 1 competition")

        # Validate structure
        first_comp = competitions[0]
        required_fields = ['id', 'title', 'url', 'deadline', 'category',
                          'reward', 'teamCount']

        for field in required_fields:
            self.assertIn(field, first_comp, f"Should have '{field}' field")

        print(f"✅ Found {len(competitions)} active competitions")
        print(f"   First: {first_comp['title']}")
        print(f"   Teams: {first_comp['teamCount']}")
        print(f"   Reward: {first_comp['reward']}")

    def test_02_rank_competitions(self):
        """Test competition ranking."""
        print("\n[TEST] Ranking competitions...")

        competitions = self.collector.get_active_competitions()
        self.assertGreater(len(competitions), 0, "Need competitions to rank")

        ranked = self.collector.rank_competitions(competitions)

        # Assertions
        self.assertIsNotNone(ranked, "Should return ranked list")
        self.assertEqual(len(ranked), len(competitions), "Should rank all competitions")

        # Check ranking fields added
        first = ranked[0]
        self.assertIn('ranking_score', first, "Should have ranking_score")
        self.assertIn('prize_value', first, "Should have prize_value")
        self.assertIn('complexity_level', first, "Should have complexity_level")

        # Check sorted by score
        if len(ranked) > 1:
            self.assertGreaterEqual(
                ranked[0]['ranking_score'],
                ranked[1]['ranking_score'],
                "Should be sorted by score descending"
            )

        print(f"✅ Ranked {len(ranked)} competitions")
        print(f"   Top competition: {first['title']}")
        print(f"   Score: {first['ranking_score']:.3f}")
        print(f"   Complexity: {first['complexity_level']}")

    def test_03_get_competition_leaderboard(self):
        """Test fetching competition leaderboard."""
        print("\n[TEST] Fetching competition leaderboard...")

        # Get a competition
        competitions = self.collector.get_active_competitions()
        self.assertGreater(len(competitions), 0, "Need competitions to test")

        # Try first few competitions (some may have private leaderboards)
        leaderboard = None
        tested_comp = None

        for comp in competitions[:5]:
            comp_id = comp['id']
            print(f"   Trying: {comp['title']} ({comp_id})")

            leaderboard = self.collector.get_competition_leaderboard(comp_id)

            if leaderboard is not None and not leaderboard.empty:
                tested_comp = comp
                break

        if leaderboard is None or leaderboard.empty:
            print("⚠️  All tested competitions have private/unavailable leaderboards")
            self.skipTest("No public leaderboards available")

        # Assertions
        self.assertIsNotNone(leaderboard, "Should return leaderboard")
        self.assertGreater(len(leaderboard), 0, "Should have entries")

        # Check columns
        required_columns = ['rank', 'teamId', 'teamName', 'score']
        for col in required_columns:
            self.assertIn(col, leaderboard.columns, f"Should have '{col}' column")

        # Validate data types
        self.assertTrue(
            leaderboard['rank'].dtype in ['int64', 'int32', 'object'],
            "Rank should be numeric or object"
        )

        # Check rank values are reasonable
        first_rank = leaderboard.iloc[0]['rank']
        self.assertGreater(first_rank, 0, "Rank should be positive")

        print(f"✅ Leaderboard fetched for: {tested_comp['title']}")
        print(f"   Entries: {len(leaderboard)}")
        print(f"   Leader: {leaderboard.iloc[0]['teamName']}")
        print(f"   Score: {leaderboard.iloc[0]['score']}")

    def test_04_get_competition_kernels(self):
        """Test fetching competition kernels."""
        print("\n[TEST] Fetching competition kernels...")

        # Get a popular competition (likely to have kernels)
        competitions = self.collector.get_active_competitions()
        self.assertGreater(len(competitions), 0, "Need competitions to test")

        # Try competitions with high team count (more likely to have kernels)
        sorted_comps = sorted(
            competitions,
            key=lambda x: x.get('teamCount', 0),
            reverse=True
        )

        kernels = None
        tested_comp = None

        for comp in sorted_comps[:5]:
            comp_id = comp['id']
            print(f"   Trying: {comp['title']} ({comp_id})")

            kernels = self.collector.get_competition_kernels(comp_id, max_kernels=5)

            if kernels and len(kernels) > 0:
                tested_comp = comp
                break

        if not kernels:
            print("⚠️  No public kernels found in tested competitions")
            self.skipTest("No public kernels available")

        # Assertions
        self.assertIsNotNone(kernels, "Should return kernels list")
        self.assertIsInstance(kernels, list, "Should be a list")
        self.assertGreater(len(kernels), 0, "Should have at least 1 kernel")

        # Check kernel structure
        first_kernel = kernels[0]
        required_fields = ['title', 'author', 'url', 'votes', 'language']

        for field in required_fields:
            self.assertIn(field, first_kernel, f"Should have '{field}' field")

        print(f"✅ Kernels fetched for: {tested_comp['title']}")
        print(f"   Count: {len(kernels)}")
        print(f"   Top kernel: {first_kernel['title']}")
        print(f"   Author: {first_kernel['author']}")
        print(f"   Votes: {first_kernel['votes']}")

    def test_05_extract_prize_value(self):
        """Test prize value extraction."""
        print("\n[TEST] Testing prize value extraction...")

        test_cases = [
            ("$100,000", 100000),
            ("$50000", 50000),
            ("25000 USD", 25000),
            ("Kudos", 0),
            ("", 0),
            ("Knowledge", 0),
        ]

        for prize_str, expected in test_cases:
            result = self.collector._extract_prize_value(prize_str)
            self.assertEqual(
                result, expected,
                f"'{prize_str}' should extract to {expected}"
            )

        print(f"✅ All {len(test_cases)} prize extraction tests passed")


class TestGitHubCollectorIntegration(unittest.TestCase):
    """Integration tests for GitHub collector."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        cls.has_credentials = bool(os.getenv('GITHUB_TOKEN'))

        if not cls.has_credentials:
            print("\n⚠️  SKIPPING GitHub tests: No token found")
            print("   Add GITHUB_TOKEN to .env file")
            print("   Note: Some tests may work without token (rate limited)")

        cls.config = ConfigLoader()
        cls.collector = GitHubCollector(cls.config)

    def test_01_search_repositories(self):
        """Test searching GitHub repositories."""
        print("\n[TEST] Searching GitHub repositories...")

        # Search for popular ML algorithm
        algorithm = "xgboost"
        repos = self.collector.search_repositories_by_algorithm(algorithm, max_repos=5)

        # Assertions
        self.assertIsNotNone(repos, "Should return repos list")
        self.assertIsInstance(repos, list, "Should be a list")

        if not self.has_credentials:
            # Without token, might hit rate limit
            if len(repos) == 0:
                print("⚠️  No repos found (may be rate limited without token)")
                self.skipTest("Rate limited - add GITHUB_TOKEN to .env")
                return

        self.assertGreater(len(repos), 0, "Should find at least 1 repo")

        # Check repo structure
        first_repo = repos[0]
        required_fields = ['name', 'url', 'description', 'stars', 'language']

        for field in required_fields:
            self.assertIn(field, first_repo, f"Should have '{field}' field")

        # Validate data
        self.assertGreater(first_repo['stars'], 0, "Should have positive stars")
        self.assertIn('http', first_repo['url'], "URL should be valid")

        print(f"✅ Found {len(repos)} repositories for '{algorithm}'")
        print(f"   Top repo: {first_repo['name']}")
        print(f"   Stars: {first_repo['stars']}")
        print(f"   Language: {first_repo['language']}")

    def test_02_discover_competition_repos(self):
        """Test discovering repos for competition."""
        print("\n[TEST] Discovering competition repositories...")

        competition = {
            'id': 'house-prices-advanced-regression-techniques',
            'title': 'House Prices - Advanced Regression Techniques',
            'category': 'Getting Started'
        }

        repos = self.collector.discover_competition_repos(competition, max_repos=3)

        # Assertions
        self.assertIsNotNone(repos, "Should return repos list")
        self.assertIsInstance(repos, list, "Should be a list")

        if not self.has_credentials and len(repos) == 0:
            print("⚠️  Rate limited - add GITHUB_TOKEN for better results")
            self.skipTest("Rate limited without token")

        print(f"✅ Found {len(repos)} repositories for competition")
        if repos:
            print(f"   First: {repos[0]['name']}")


class TestResearchCollectorIntegration(unittest.TestCase):
    """Integration tests for Research/arXiv collector."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        cls.config = ConfigLoader()
        cls.collector = ResearchCollector(cls.config)

    def test_01_fetch_recent_papers(self):
        """Test fetching recent research papers."""
        print("\n[TEST] Fetching recent research papers from arXiv...")

        papers = self.collector.fetch_recent_papers(max_results=5)

        # Assertions
        self.assertIsNotNone(papers, "Should return papers list")
        self.assertIsInstance(papers, list, "Should be a list")
        self.assertGreater(len(papers), 0, "Should find at least 1 paper")

        # Check paper structure
        first_paper = papers[0]
        required_fields = ['title', 'authors', 'summary', 'url', 'published']

        for field in required_fields:
            self.assertIn(field, first_paper, f"Should have '{field}' field")

        # Validate data
        self.assertIsInstance(first_paper['authors'], list, "Authors should be list")
        self.assertGreater(len(first_paper['authors']), 0, "Should have authors")
        self.assertIn('arxiv.org', first_paper['url'], "URL should be arXiv")

        print(f"✅ Found {len(papers)} recent papers")
        print(f"   Latest: {first_paper['title'][:60]}...")
        print(f"   Authors: {', '.join(first_paper['authors'][:2])}")
        print(f"   Published: {first_paper['published']}")

    def test_02_search_papers_by_keyword(self):
        """Test searching papers by keyword."""
        print("\n[TEST] Searching papers by keyword...")

        keyword = "machine learning"
        papers = self.collector.search_papers(keyword, max_results=3)

        # Assertions
        self.assertIsNotNone(papers, "Should return papers list")
        self.assertIsInstance(papers, list, "Should be a list")
        self.assertGreater(len(papers), 0, "Should find at least 1 paper")

        # Check relevance
        first_paper = papers[0]
        content = f"{first_paper['title']} {first_paper['summary']}".lower()

        # At least one search term should appear
        search_terms = keyword.lower().split()
        has_term = any(term in content for term in search_terms)
        self.assertTrue(has_term, "Paper should be relevant to search")

        print(f"✅ Found {len(papers)} papers for '{keyword}'")
        print(f"   First: {first_paper['title'][:60]}...")

    def test_03_filter_by_category(self):
        """Test filtering papers by category."""
        print("\n[TEST] Filtering papers by category...")

        # Get papers and check categories
        papers = self.collector.fetch_recent_papers(max_results=10)

        ml_papers = [p for p in papers if 'cs.LG' in p.get('categories', [])]

        if ml_papers:
            print(f"✅ Found {len(ml_papers)} ML papers out of {len(papers)}")
            print(f"   Example categories: {ml_papers[0].get('categories', [])}")
        else:
            print("⚠️  No ML papers in recent results (timing dependent)")


class TestCollectorsEndToEnd(unittest.TestCase):
    """End-to-end integration tests combining multiple collectors."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        load_dotenv()
        cls.config = ConfigLoader()

        # Check which collectors we can test
        cls.has_kaggle = bool(
            os.getenv('KAGGLE_USERNAME') and os.getenv('KAGGLE_KEY')
        ) or os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json'))

        cls.has_github = bool(os.getenv('GITHUB_TOKEN'))

        # Research (arXiv) doesn't need credentials
        cls.has_research = True

    def test_01_kaggle_to_github_workflow(self):
        """Test workflow: Get Kaggle comp → Find GitHub repos."""
        if not self.has_kaggle:
            self.skipTest("Kaggle credentials not configured")

        print("\n[TEST] End-to-end: Kaggle → GitHub workflow...")

        # Step 1: Get Kaggle competition
        kaggle = KaggleCollector(self.config)
        competitions = kaggle.get_active_competitions()
        self.assertGreater(len(competitions), 0, "Need competitions")

        competition = competitions[0]
        print(f"   Kaggle competition: {competition['title']}")

        # Step 2: Find related GitHub repos
        if not self.has_github:
            print("   ⚠️  Skipping GitHub search (no token)")
            return

        github = GitHubCollector(self.config)
        repos = github.discover_competition_repos(competition, max_repos=3)

        print(f"   Found {len(repos)} related repos")
        if repos:
            print(f"   Top repo: {repos[0]['name']}")

        print("✅ Kaggle → GitHub workflow successful")

    def test_02_research_relevance_check(self):
        """Test getting research papers relevant to competitions."""
        print("\n[TEST] End-to-end: Research paper relevance...")

        # Get recent research
        research = ResearchCollector(self.config)
        papers = research.fetch_recent_papers(max_results=10)

        self.assertGreater(len(papers), 0, "Should find papers")

        # Check if papers are ML-related
        ml_keywords = ['machine learning', 'neural', 'deep learning',
                      'classification', 'regression', 'model']

        relevant_count = 0
        for paper in papers:
            content = f"{paper['title']} {paper['summary']}".lower()
            if any(kw in content for kw in ml_keywords):
                relevant_count += 1

        relevance_rate = relevant_count / len(papers) * 100

        print(f"   Papers fetched: {len(papers)}")
        print(f"   ML-relevant: {relevant_count} ({relevance_rate:.1f}%)")
        print("✅ Research papers relevance check complete")

    def test_03_data_completeness_check(self):
        """Test that all collectors return complete data structures."""
        print("\n[TEST] Data completeness check across collectors...")

        results = {}

        # Kaggle
        if self.has_kaggle:
            kaggle = KaggleCollector(self.config)
            comps = kaggle.get_active_competitions()
            results['kaggle'] = len(comps) > 0 and all(
                'title' in c and 'id' in c for c in comps
            )
        else:
            results['kaggle'] = None

        # GitHub
        github = GitHubCollector(self.config)
        repos = github.search_repositories_by_algorithm('xgboost', max_repos=2)
        results['github'] = len(repos) > 0 and all(
            'name' in r and 'url' in r for r in repos
        ) if repos else False

        # Research
        research = ResearchCollector(self.config)
        papers = research.fetch_recent_papers(max_results=2)
        results['research'] = len(papers) > 0 and all(
            'title' in p and 'authors' in p for p in papers
        )

        # Summary
        for collector, is_complete in results.items():
            if is_complete is None:
                print(f"   {collector}: SKIPPED (no credentials)")
            elif is_complete:
                print(f"   {collector}: ✅ COMPLETE")
            else:
                print(f"   {collector}: ❌ INCOMPLETE")

        # At least research should work
        self.assertTrue(
            results['research'],
            "Research collector should return complete data"
        )

        print("✅ Data completeness check complete")


def run_integration_tests():
    """Run integration tests with summary."""
    print("\n" + "=" * 70)
    print(" INTEGRATION TESTS - ALL COLLECTORS")
    print("=" * 70)

    # Check credentials
    load_dotenv()

    print("\nCredential Status:")
    print(f"  Kaggle: {'✅' if os.getenv('KAGGLE_USERNAME') else '❌'}")
    print(f"  GitHub: {'✅' if os.getenv('GITHUB_TOKEN') else '⚠️  (optional)'}")
    print(f"  Gemini: {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}")
    print(f"  arXiv:  ✅ (no credentials needed)")

    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKaggleCollectorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestGitHubCollectorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestResearchCollectorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCollectorsEndToEnd))

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_integration_tests())
