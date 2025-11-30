"""Unit tests for Gemini Generator."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generators.gemini_generator import GeminiGenerator
from src.utils.config_loader import ConfigLoader


class TestGeminiGenerator(unittest.TestCase):
    """Test cases for GeminiGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=ConfigLoader)
        self.config.get_env.return_value = "test-api-key"
        self.config.get.side_effect = lambda key, default=None: {
            'gemini.model': 'gemini-1.5-flash',
            'gemini.retry_attempts': 3,
            'gemini.retry_delay': 1,
            'gemini.temperature': 0.7,
            'gemini.max_tokens': 8000,
        }.get(key, default)

    @patch('src.generators.gemini_generator.genai')
    def test_initialization_success(self, mock_genai):
        """Test successful initialization."""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)

        self.assertIsNotNone(generator)
        mock_genai.configure.assert_called_once_with(api_key="test-api-key")
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-flash')

    @patch('src.generators.gemini_generator.genai')
    def test_initialization_no_api_key(self, mock_genai):
        """Test initialization fails without API key."""
        self.config.get_env.return_value = None

        with self.assertRaises(ValueError) as context:
            GeminiGenerator(self.config)

        self.assertIn("GEMINI_API_KEY", str(context.exception))

    @patch('src.generators.gemini_generator.genai')
    def test_generate_competition_overview(self, mock_genai):
        """Test competition overview generation."""
        mock_response = Mock()
        mock_response.text = "Generated overview text"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)

        competitions = [
            {
                'title': 'Test Competition',
                'reward': '$10,000',
                'teamCount': 100,
                'complexity_level': 'High'
            }
        ]

        result = generator.generate_competition_overview(competitions)

        self.assertEqual(result, "Generated overview text")
        mock_model.generate_content.assert_called_once()

    @patch('src.generators.gemini_generator.genai')
    @patch('src.generators.gemini_generator.time.sleep')
    def test_generate_with_retry_success_on_second_attempt(self, mock_sleep, mock_genai):
        """Test retry logic succeeds on second attempt."""
        mock_response = Mock()
        mock_response.text = "Success after retry"

        mock_model = Mock()
        # First call raises exception, second succeeds
        mock_model.generate_content.side_effect = [
            Exception("Temporary error"),
            mock_response
        ]
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test prompt")

        self.assertEqual(result, "Success after retry")
        self.assertEqual(mock_model.generate_content.call_count, 2)
        mock_sleep.assert_called_once()

    @patch('src.generators.gemini_generator.genai')
    @patch('src.generators.gemini_generator.time.sleep')
    def test_generate_with_retry_all_attempts_fail(self, mock_sleep, mock_genai):
        """Test all retry attempts fail."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("Persistent error")
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test prompt")

        self.assertIn("Content generation failed", result)
        self.assertEqual(mock_model.generate_content.call_count, 3)

    @patch('src.generators.gemini_generator.genai')
    def test_generate_with_empty_response(self, mock_genai):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.text = ""

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test prompt")

        self.assertIn("Content generation failed", result)

    @patch('src.generators.gemini_generator.genai')
    def test_authentication_error_handling(self, mock_genai):
        """Test authentication error handling."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API key not valid")
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test prompt")

        self.assertIn("Authentication error", result)


class TestGeminiGeneratorIntegration(unittest.TestCase):
    """Integration tests for Gemini Generator (requires real API key)."""

    def setUp(self):
        """Set up test fixtures."""
        import os
        self.api_key = os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            self.skipTest("GEMINI_API_KEY not set - skipping integration tests")

        self.config = Mock(spec=ConfigLoader)
        self.config.get_env.return_value = self.api_key
        self.config.get.side_effect = lambda key, default=None: {
            'gemini.model': 'gemini-1.5-flash',
            'gemini.retry_attempts': 3,
            'gemini.retry_delay': 1,
            'gemini.temperature': 0.7,
            'gemini.max_tokens': 1000,
        }.get(key, default)

    def test_real_generation(self):
        """Test real generation with actual API."""
        generator = GeminiGenerator(self.config)

        competitions = [
            {
                'title': 'Machine Learning Competition',
                'reward': '$10,000',
                'teamCount': 150,
                'complexity_level': 'High'
            },
            {
                'title': 'Computer Vision Challenge',
                'reward': '$5,000',
                'teamCount': 80,
                'complexity_level': 'Medium'
            }
        ]

        result = generator.generate_competition_overview(competitions)

        # Verify response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 50)
        self.assertNotIn("[Content generation failed", result)
        print(f"\n✅ Real API test passed. Generated {len(result)} characters")


if __name__ == '__main__':
    unittest.main()
