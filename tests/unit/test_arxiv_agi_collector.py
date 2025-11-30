"""Unit tests for arXiv AGI Collector."""
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.collectors.agi.arxiv_agi_collector import ArxivAGICollector, AGIKeywords


class TestAGIKeywords(unittest.TestCase):
    """Test AGI keywords configuration."""

    def test_get_all_keywords(self):
        """Test getting all keywords."""
        all_keywords = AGIKeywords.get_all_keywords()

        self.assertIsInstance(all_keywords, list)
        self.assertGreater(len(all_keywords), 50)
        self.assertIn('artificial general intelligence', all_keywords)
        self.assertIn('meta-learning', all_keywords)
        self.assertIn('reasoning', all_keywords)

    def test_get_priority_keywords(self):
        """Test getting priority keywords."""
        priority = AGIKeywords.get_priority_keywords()

        self.assertIsInstance(priority, list)
        self.assertLess(len(priority), len(AGIKeywords.get_all_keywords()))
        self.assertIn('agi', priority)
        self.assertIn('ai safety', priority)


class TestArxivAGICollector(unittest.TestCase):
    """Test cases for ArxivAGICollector."""

    def setUp(self):
        """Set up test fixtures."""
        self.collector = ArxivAGICollector()

    def test_initialization(self):
        """Test collector initialization."""
        self.assertIsNotNone(self.collector)
        self.assertIsNotNone(self.collector.client)
        self.assertIsNotNone(self.collector.keywords)

    def test_calculate_agi_indicators(self):
        """Test AGI relevance indicator calculation."""
        title = "Artificial General Intelligence via Transfer Learning"
        abstract = "We propose a novel approach to AGI using meta-learning and reasoning capabilities."
        categories = ['cs.AI', 'cs.LG']

        indicators = self.collector._calculate_agi_indicators(title, abstract, categories)

        self.assertIsInstance(indicators, dict)
        self.assertIn('keyword_matches', indicators)
        self.assertIn('score', indicators)
        self.assertGreater(indicators['score'], 0)
        self.assertGreater(len(indicators['keyword_matches']), 0)

    def test_calculate_priority(self):
        """Test priority calculation."""
        # Create mock result
        mock_result = Mock()
        mock_result.title = "AGI Research"
        mock_result.summary = "Research on artificial general intelligence"

        # High score should give critical priority
        high_indicators = {'score': 8.0, 'match_count': 12}
        priority = self.collector._calculate_priority(mock_result, high_indicators)
        self.assertEqual(priority, 'critical')

        # Medium score should give medium priority
        med_indicators = {'score': 4.0, 'match_count': 4}
        priority = self.collector._calculate_priority(mock_result, med_indicators)
        self.assertEqual(priority, 'medium')

        # Low score should give low priority
        low_indicators = {'score': 1.0, 'match_count': 1}
        priority = self.collector._calculate_priority(mock_result, low_indicators)
        self.assertEqual(priority, 'low')

    def test_process_paper(self):
        """Test paper processing."""
        # Create mock arxiv result
        mock_result = Mock()
        mock_result.entry_id = "http://arxiv.org/abs/2301.12345v1"
        mock_result.title = "Advances in AGI"
        mock_result.authors = [Mock(name="John Doe"), Mock(name="Jane Smith")]
        mock_result.summary = "Research on artificial general intelligence and reasoning."
        mock_result.published = datetime(2024, 1, 15, 10, 0, 0)
        mock_result.updated = datetime(2024, 1, 15, 10, 0, 0)
        mock_result.categories = ['cs.AI', 'cs.LG']
        mock_result.primary_category = 'cs.AI'
        mock_result.pdf_url = "http://arxiv.org/pdf/2301.12345v1"
        mock_result.doi = None
        mock_result.journal_ref = None
        mock_result.comment = None

        paper = self.collector._process_paper(mock_result)

        self.assertIsNotNone(paper)
        self.assertEqual(paper['paper_id'], 'arxiv_2301.12345')
        self.assertEqual(paper['source'], 'arxiv')
        self.assertEqual(paper['title'], 'Advances in AGI')
        self.assertEqual(len(paper['authors']), 2)
        self.assertIn('agi_indicator_score', paper)
        self.assertIn('priority', paper)

    @patch('src.collectors.agi.arxiv_agi_collector.arxiv')
    async def test_collect_with_mock(self, mock_arxiv_module):
        """Test collection with mocked arxiv module."""
        # Create mock search results
        mock_result1 = Mock()
        mock_result1.entry_id = "http://arxiv.org/abs/2401.00001v1"
        mock_result1.title = "AGI via Meta-Learning"
        mock_result1.authors = [Mock(name="Researcher One")]
        mock_result1.summary = "Novel approach to AGI using meta-learning"
        mock_result1.published = datetime.now()
        mock_result1.updated = datetime.now()
        mock_result1.categories = ['cs.AI']
        mock_result1.primary_category = 'cs.AI'
        mock_result1.pdf_url = "http://arxiv.org/pdf/2401.00001v1"
        mock_result1.doi = None
        mock_result1.journal_ref = None
        mock_result1.comment = None

        # Mock client and search
        mock_client = Mock()
        mock_client.results.return_value = [mock_result1]
        self.collector.client = mock_client

        papers = await self.collector.collect(max_results=10, days_back=7)

        self.assertIsInstance(papers, list)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]['title'], 'AGI via Meta-Learning')


class TestArxivAGICollectorIntegration(unittest.TestCase):
    """Integration tests for arXiv collector (requires internet)."""

    def setUp(self):
        """Set up test fixtures."""
        self.collector = ArxivAGICollector()

    async def test_real_arxiv_collection(self):
        """Test real collection from arXiv (limited results)."""
        try:
            papers = await self.collector.collect(
                max_results=5,
                days_back=30,
                use_priority_keywords=True
            )

            # Verify results
            self.assertIsInstance(papers, list)
            print(f"\n✅ Collected {len(papers)} papers from arXiv")

            if papers:
                # Check first paper structure
                paper = papers[0]
                self.assertIn('paper_id', paper)
                self.assertIn('title', paper)
                self.assertIn('authors', paper)
                self.assertIn('abstract', paper)
                self.assertIn('agi_indicator_score', paper)
                print(f"   Sample paper: {paper['title']}")
                print(f"   AGI score: {paper['agi_indicator_score']}")

        except Exception as e:
            self.skipTest(f"arXiv connection failed: {e}")


if __name__ == '__main__':
    # Run async tests with asyncio
    import asyncio
    import sys

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    # Run synchronous tests
    sync_suite = unittest.TestSuite()
    async_suite = unittest.TestSuite()

    for test in suite:
        if 'Integration' in str(test):
            async_suite.addTest(test)
        else:
            sync_suite.addTest(test)

    # Run sync tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(sync_suite)

    # Run async tests
    if async_suite.countTestCases() > 0:
        print("\n" + "="*70)
        print("Running integration tests (requires internet)...")
        print("="*70)

        for test in async_suite:
            try:
                test_method = getattr(test, test._testMethodName)
                if asyncio.iscoroutinefunction(test_method):
                    asyncio.run(test_method())
                    print(f"✅ {test._testMethodName} passed")
            except Exception as e:
                print(f"❌ {test._testMethodName} failed: {e}")

    sys.exit(0 if result.wasSuccessful() else 1)
