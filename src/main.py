"""Main entry point for Kaggle daily blog generation."""
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger
from src.generators.blog_generator import BlogGenerator
from src.utils.error_handler import ErrorHandler


logger = setup_logger("main")


def main():
    """Main execution function."""
    logger.info("=" * 80)
    logger.info("Starting Kaggle Daily Blog Generation")
    logger.info("=" * 80)

    try:
        # Load configuration
        config = ConfigLoader()
        logger.info("Configuration loaded successfully")

        # Initialize error handler
        error_handler = ErrorHandler(config)

        # Initialize blog generator
        generator = BlogGenerator(config)

        # Generate blog
        result = generator.generate_daily_blog()

        logger.info("=" * 80)
        logger.info("Blog Generation Completed Successfully")
        logger.info(f"Markdown: {result['paths']['markdown']}")
        logger.info(f"HTML: {result['paths']['html']}")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error("=" * 80)
        logger.error("Blog Generation Failed")
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("=" * 80)

        # Handle error
        try:
            error_handler = ErrorHandler(config)
            error_handler.handle_error(e, context="Blog Generation")
        except Exception as handler_error:
            logger.error(f"Error handler also failed: {handler_error}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
