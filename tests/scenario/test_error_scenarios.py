"""Scenario tests for error handling and edge cases."""
import unittest
from unittest.mock import Mock, patch
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generators.gemini_generator import GeminiGenerator
from src.utils.config_loader import ConfigLoader


class TestErrorScenarios(unittest.TestCase):
    """Test error handling scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=ConfigLoader)
        self.config.get_env.return_value = "test-api-key"
        self.config.get.side_effect = lambda key, default=None: {
            'gemini.model': 'gemini-1.5-flash',
            'gemini.retry_attempts': 3,
            'gemini.retry_delay': 0.1,  # Fast retries for testing
            'gemini.temperature': 0.7,
            'gemini.max_tokens': 1000,
        }.get(key, default)

    @patch('src.generators.gemini_generator.genai')
    def test_api_quota_exceeded(self, mock_genai):
        """Test handling of quota exceeded error."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("quota exceeded for requests")
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test prompt")

        self.assertIn("Rate limit exceeded", result)

    @patch('src.generators.gemini_generator.genai')
    def test_api_authentication_failure(self, mock_genai):
        """Test handling of authentication failure."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API key not valid")
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test prompt")

        self.assertIn("Authentication error", result)

    @patch('src.generators.gemini_generator.genai')
    def test_malformed_response(self, mock_genai):
        """Test handling of malformed response."""
        mock_response = Mock()
        del mock_response.text  # Remove text attribute

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test prompt")

        self.assertIn("Content generation failed", result)

    @patch('src.generators.gemini_generator.genai')
    def test_network_timeout(self, mock_genai):
        """Test handling of network timeout."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("Connection timeout")
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test prompt")

        self.assertIn("Content generation failed", result)

    @patch('src.generators.gemini_generator.genai')
    def test_empty_competitions_list(self, mock_genai):
        """Test handling of empty competitions list."""
        mock_response = Mock()
        mock_response.text = "No competitions available"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator.generate_competition_overview([])

        self.assertIsInstance(result, str)
        # Should handle gracefully even with empty list

    @patch('src.generators.gemini_generator.genai')
    def test_malformed_competition_data(self, mock_genai):
        """Test handling of malformed competition data."""
        mock_response = Mock()
        mock_response.text = "Generated content"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)

        # Missing required fields
        bad_competitions = [
            {'title': 'Test'},  # Missing other fields
            {},  # Empty dict
        ]

        # Should not crash
        result = generator.generate_competition_overview(bad_competitions)
        self.assertIsInstance(result, str)

    def test_missing_environment_variable(self):
        """Test handling of missing environment variable."""
        config = Mock(spec=ConfigLoader)
        config.get_env.return_value = None

        with self.assertRaises(ValueError) as context:
            GeminiGenerator(config)

        self.assertIn("GEMINI_API_KEY", str(context.exception))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=ConfigLoader)
        self.config.get_env.return_value = "test-api-key"
        self.config.get.side_effect = lambda key, default=None: {
            'gemini.model': 'gemini-1.5-flash',
            'gemini.retry_attempts': 1,  # Single attempt for edge case testing
            'gemini.retry_delay': 0.1,
            'gemini.temperature': 0.7,
            'gemini.max_tokens': 100,
        }.get(key, default)

    @patch('src.generators.gemini_generator.genai')
    def test_very_long_prompt(self, mock_genai):
        """Test handling of very long prompts."""
        mock_response = Mock()
        mock_response.text = "Truncated response"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)

        # Create very long prompt
        long_prompt = "Test prompt " * 10000

        result = generator._generate_with_retry(long_prompt)
        self.assertIsInstance(result, str)

    @patch('src.generators.gemini_generator.genai')
    def test_special_characters_in_content(self, mock_genai):
        """Test handling of special characters."""
        mock_response = Mock()
        mock_response.text = "Response with émojis 🚀 and spëcial çhars"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)

        competitions = [
            {
                'title': 'Test © Competition™ with émojis 🎯',
                'reward': '$10,000',
                'teamCount': 100,
                'complexity_level': 'High'
            }
        ]

        result = generator.generate_competition_overview(competitions)
        self.assertIsInstance(result, str)

    @patch('src.generators.gemini_generator.genai')
    def test_unicode_handling(self, mock_genai):
        """Test Unicode text handling."""
        mock_response = Mock()
        mock_response.text = "Résumé: 日本語 中文 한국어 العربية"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = GeminiGenerator(self.config)
        result = generator._generate_with_retry("Test")

        self.assertIsInstance(result, str)
        self.assertIn("日本語", result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
