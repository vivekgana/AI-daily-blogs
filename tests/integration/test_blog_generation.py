"""Integration tests for blog generation workflow."""
import unittest
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import ConfigLoader
from src.generators.blog_generator import BlogGenerator


class TestBlogGenerationIntegration(unittest.TestCase):
    """Integration tests for complete blog generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            self.skipTest("GEMINI_API_KEY not set - skipping integration tests")

        # Load real config
        try:
            self.config = ConfigLoader()
            print(f"✅ Configuration loaded successfully")
        except Exception as e:
            self.skipTest(f"Failed to load configuration: {e}")

    def test_blog_generation_complete_flow(self):
        """Test complete blog generation workflow."""
        try:
            # Initialize blog generator
            generator = BlogGenerator(self.config)
            print(f"✅ Blog generator initialized")

            # Generate blog
            print(f"\n🔄 Starting blog generation...")
            result = generator.generate_daily_blog()

            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn('paths', result)
            self.assertIn('metadata', result)

            # Verify files were created
            markdown_path = result['paths']['markdown']
            html_path = result['paths']['html']

            self.assertTrue(Path(markdown_path).exists(), f"Markdown file not created: {markdown_path}")
            self.assertTrue(Path(html_path).exists(), f"HTML file not created: {html_path}")

            # Check file sizes
            md_size = Path(markdown_path).stat().st_size
            html_size = Path(html_path).stat().st_size

            self.assertGreater(md_size, 500, "Markdown file too small")
            self.assertGreater(html_size, 500, "HTML file too small")

            print(f"\n✅ Blog generation successful!")
            print(f"   Markdown: {markdown_path} ({md_size} bytes)")
            print(f"   HTML: {html_path} ({html_size} bytes)")
            print(f"   Competitions: {result['metadata'].get('total_competitions', 0)}")

        except Exception as e:
            self.fail(f"Blog generation failed: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
