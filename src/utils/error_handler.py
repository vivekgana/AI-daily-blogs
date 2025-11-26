"""Error handling and notification system."""
import os
import time
import traceback
from typing import Optional
from datetime import datetime

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader


logger = setup_logger("error_handler")


class ErrorHandler:
    """Handle errors and send notifications."""

    def __init__(self, config: ConfigLoader):
        """Initialize error handler.

        Args:
            config: Configuration loader instance
        """
        self.config = config
        self.max_retries = config.get('error_handling.max_retries', 3)
        self.retry_delay = config.get('error_handling.retry_delay', 300)

    def handle_error(self, error: Exception, context: str = "Unknown"):
        """Handle an error with notifications.

        Args:
            error: The exception that occurred
            context: Context where error occurred
        """
        logger.error(f"Handling error in {context}: {str(error)}")

        error_details = {
            'context': context,
            'error': str(error),
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc()
        }

        # Send email notification
        if self.config.get('error_handling.send_email_on_failure', True):
            self._send_email_notification(error_details)

        # Create GitHub issue
        if self.config.get('error_handling.create_github_issue', True):
            self._create_github_issue(error_details)

    def _send_email_notification(self, error_details: dict):
        """Send email notification about error.

        Args:
            error_details: Dictionary with error information
        """
        try:
            # Email will be sent via GitHub Actions workflow
            # We'll create a flag file that the workflow can detect
            logger.info("Email notification would be sent via GitHub Actions")

        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    def _create_github_issue(self, error_details: dict):
        """Create GitHub issue for error.

        Args:
            error_details: Dictionary with error information
        """
        try:
            # GitHub issue will be created via GitHub Actions
            # We'll create a marker file that can be detected
            logger.info("GitHub issue would be created via GitHub Actions")

            # Save error details to file for GitHub Actions
            error_file = f"error_{int(time.time())}.json"
            import json
            with open(error_file, 'w') as f:
                json.dump(error_details, f, indent=2)

            logger.info(f"Error details saved to {error_file}")

        except Exception as e:
            logger.error(f"Failed to create GitHub issue marker: {e}")

    def retry_with_backoff(self, func, *args, **kwargs):
        """Retry a function with exponential backoff.

        Args:
            func: Function to retry
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries}")
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

        # All retries failed
        if last_exception:
            raise last_exception
