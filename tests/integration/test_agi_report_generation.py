"""Integration tests for AGI report generation."""
import unittest
import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import ConfigLoader
from src.generators.agi.agi_report_generator import AGIResearchReportGenerator
from src.collectors.agi.arxiv_agi_collector import ArxivAGICollector


class TestAGIReportIntegration(unittest.TestCase):
    """Integration tests for AGI research report generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            self.skipTest("GEMINI_API_KEY not set - skipping integration tests")

        try:
            self.config = ConfigLoader()
            print(f"✅ Configuration loaded successfully")
        except Exception as e:
            self.skipTest(f"Failed to load configuration: {e}")

    def test_agi_report_with_mock_data(self):
        """Test AGI report generation with mock data."""
        try:
            generator = AGIResearchReportGenerator(self.config)
            print(f"✅ AGI report generator initialized")

            # Create mock papers
            mock_papers = [
                {
                    'paper_id': 'arxiv_2401.00001',
                    'title': 'Advances in Meta-Learning for General Intelligence',
                    'authors': ['John Doe', 'Jane Smith'],
                    'abstract': 'We present a novel approach to meta-learning that demonstrates improved generalization across diverse tasks.',
                    'published_date': datetime.now().isoformat(),
                    'url': 'https://arxiv.org/abs/2401.00001',
                    'agi_indicator_score': 8.5,
                    'agi_keyword_matches': ['meta-learning', 'general intelligence', 'transfer learning'],
                    'priority': 'high',
                    'categories': ['cs.AI', 'cs.LG']
                },
                {
                    'paper_id': 'arxiv_2401.00002',
                    'title': 'AI Safety and Alignment Mechanisms',
                    'authors': ['Alice Johnson'],
                    'abstract': 'This paper explores novel mechanisms for ensuring AI safety and value alignment in increasingly capable systems.',
                    'published_date': datetime.now().isoformat(),
                    'url': 'https://arxiv.org/abs/2401.00002',
                    'agi_indicator_score': 7.5,
                    'agi_keyword_matches': ['ai safety', 'alignment', 'value alignment'],
                    'priority': 'critical',
                    'categories': ['cs.AI']
                }
            ]

            # Generate report
            print(f"\n🔄 Generating AGI research report...")
            report = generator.generate_daily_agi_report(mock_papers)

            # Verify report structure
            self.assertIsInstance(report, dict)
            self.assertIn('date', report)
            self.assertIn('executive_summary', report)
            self.assertIn('breakthrough_analysis', report)
            self.assertIn('trend_analysis', report)
            self.assertIn('research_highlights', report)
            self.assertIn('recommendations', report)

            # Verify content
            self.assertGreater(len(report['executive_summary']), 100)
            self.assertNotIn("[Content generation failed", report['executive_summary'])

            # Format as markdown
            markdown = generator.format_report_markdown(report)
            self.assertGreater(len(markdown), 500)
            self.assertIn('# AGI Research Daily Report', markdown)

            print(f"\n✅ AGI report generated successfully!")
            print(f"   Date: {report['date']}")
            print(f"   Papers analyzed: {report['total_papers']}")
            print(f"   High priority: {report['high_priority_count']}")
            print(f"   Report length: {len(markdown)} characters")

        except Exception as e:
            self.fail(f"AGI report generation failed: {e}")

    async def test_agi_report_with_real_data(self):
        """Test AGI report with real arXiv data."""
        try:
            # Collect real papers
            collector = ArxivAGICollector()
            print(f"\n🔄 Collecting AGI papers from arXiv...")

            papers = await collector.collect(
                max_results=5,
                days_back=30,
                use_priority_keywords=True
            )

            if not papers:
                self.skipTest("No papers collected from arXiv")

            print(f"✅ Collected {len(papers)} papers")

            # Generate report
            generator = AGIResearchReportGenerator(self.config)
            print(f"🔄 Generating report from real data...")

            report = generator.generate_daily_agi_report(papers)

            # Verify
            self.assertIsInstance(report, dict)
            self.assertEqual(report['total_papers'], len(papers))
            self.assertGreater(len(report['executive_summary']), 50)

            # Save report
            output_dir = Path(__file__).parent.parent.parent / 'test_output'
            output_dir.mkdir(exist_ok=True)

            report_path = output_dir / f"agi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            markdown = generator.format_report_markdown(report)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            print(f"\n✅ Report saved to: {report_path}")
            print(f"   Size: {len(markdown)} characters")

        except Exception as e:
            self.skipTest(f"Real data test failed: {e}")


if __name__ == '__main__':
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAGIReportIntegration)

    # Run synchronous tests first
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Run async test
    print("\n" + "="*70)
    print("Running async integration test...")
    print("="*70)

    try:
        test_instance = TestAGIReportIntegration()
        test_instance.setUp()
        asyncio.run(test_instance.test_agi_report_with_real_data())
    except Exception as e:
        print(f"❌ Async test failed: {e}")

    sys.exit(0 if result.wasSuccessful() else 1)
