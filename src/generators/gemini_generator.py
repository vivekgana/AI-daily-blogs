"""Google Gemini AI content generator."""
import time
from typing import Dict, Any, List
import google.generativeai as genai

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader


logger = setup_logger("gemini_generator")


class GeminiGenerator:
    """Generate content using Google Gemini AI."""

    def __init__(self, config: ConfigLoader):
        """Initialize Gemini generator.

        Args:
            config: Configuration loader instance
        """
        self.config = config
        self.last_request_time = 0  # Track last API call time for rate limiting

        # Configure Gemini API
        api_key = config.get_env('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

        # Use stable Gemini model names
        # Gemini 2.5 is the latest stable version (as of 2025)
        model_name = config.get('gemini.model', 'gemini-2.5-flash')

        # Validate model name - use stable model names
        valid_models = [
            'gemini-2.5-flash',      # Recommended: Latest fast model
            'gemini-2.5-pro',        # Latest pro model
            'gemini-2.0-flash',      # Previous generation
            'gemini-flash-latest',   # Auto-updated to latest
            'gemini-pro-latest',     # Auto-updated to latest
            'gemini-1.5-flash',      # Legacy support
            'gemini-1.5-pro',        # Legacy support
            'gemini-pro'             # Legacy support
        ]
        if model_name not in valid_models:
            logger.warning(f"Invalid model name '{model_name}', defaulting to 'gemini-2.5-flash'")
            model_name = 'gemini-2.5-flash'

        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Gemini AI initialized successfully with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model '{model_name}': {e}")
            # Try fallback models in order
            fallback_models = ['gemini-2.5-flash', 'gemini-flash-latest', 'gemini-2.0-flash', 'gemini-1.5-flash']
            for fallback in fallback_models:
                try:
                    logger.info(f"Attempting fallback to model: {fallback}")
                    self.model = genai.GenerativeModel(fallback)
                    logger.info(f"Successfully fell back to model: {fallback}")
                    model_name = fallback
                    break
                except Exception as fallback_error:
                    logger.warning(f"Fallback to {fallback} failed: {fallback_error}")
                    continue
            else:
                # If all fallbacks fail, raise the original error
                raise ValueError(f"Failed to initialize any Gemini model. Last error: {e}")

    def generate_competition_overview(
        self,
        competitions: List[Dict[str, Any]]
    ) -> str:
        """Generate competition overview section.

        Args:
            competitions: List of competition dictionaries

        Returns:
            Generated overview text
        """
        logger.info("Generating competition overview...")

        # Prepare competition data
        comp_summary = "\n".join([
            f"{i+1}. {comp['title']} - Prize: {comp.get('reward', 'N/A')}, "
            f"Teams: {comp.get('teamCount', 0)}, Complexity: {comp.get('complexity_level', 'N/A')}"
            for i, comp in enumerate(competitions[:10])
        ])

        prompt = f"""
You are a data science research engineer writing a daily blog about Kaggle competitions.

Generate a comprehensive overview section for today's top 10 Kaggle competitions.
Make it engaging, informative, and highlight key insights.

Top 10 Competitions:
{comp_summary}

Requirements:
- Write in professional yet accessible tone
- Highlight interesting patterns or trends across competitions
- Mention prize pools, team participation, and complexity levels
- Keep it concise but informative (2-3 paragraphs)
- Use hyperlinks format: [Competition Title](URL) for each competition
"""

        return self._generate_with_retry(prompt)

    def generate_leaderboard_analysis(
        self,
        competition: Dict[str, Any],
        leaderboard_df: Any
    ) -> str:
        """Generate leaderboard analysis.

        Args:
            competition: Competition dictionary
            leaderboard_df: Leaderboard dataframe

        Returns:
            Generated analysis text
        """
        logger.info(f"Generating leaderboard analysis for {competition['title']}...")

        if leaderboard_df is None or leaderboard_df.empty:
            return f"Leaderboard data not available for {competition['title']}."

        # Get top teams
        top_teams = leaderboard_df.head(5).to_dict('records') if hasattr(leaderboard_df, 'head') else []

        prompt = f"""
Analyze the current leaderboard for the Kaggle competition: {competition['title']}

Top 5 Teams:
{self._format_leaderboard(top_teams)}

Generate a brief analysis covering:
- Current leader and their score
- Competition intensity (score gaps between teams)
- Notable patterns or trends
- Keep it concise (1-2 paragraphs)
"""

        return self._generate_with_retry(prompt)

    def generate_algorithm_summary(
        self,
        competition: Dict[str, Any],
        kernels: List[Dict[str, Any]]
    ) -> str:
        """Generate algorithm summary from kernels.

        Args:
            competition: Competition dictionary
            kernels: List of kernel dictionaries

        Returns:
            Generated summary text
        """
        logger.info(f"Generating algorithm summary for {competition['title']}...")

        if not kernels:
            return f"No public kernels available yet for {competition['title']}."

        kernel_summary = "\n".join([
            f"- {k['title']} by {k['author']} ({k['votes']} votes) - {k['language']}"
            for k in kernels[:5]
        ])

        prompt = f"""
Summarize the popular algorithms and techniques being used in the Kaggle competition: {competition['title']}

Top Public Kernels:
{kernel_summary}

Generate a technical summary covering:
- Common algorithms and techniques
- Programming languages being used
- Notable approaches or innovations
- Keep it technical but accessible (2 paragraphs)
"""

        return self._generate_with_retry(prompt)

    def generate_research_summary(
        self,
        papers: List[Dict[str, Any]]
    ) -> str:
        """Generate research papers summary.

        Args:
            papers: List of paper dictionaries

        Returns:
            Generated summary text
        """
        logger.info("Generating research papers summary...")

        if not papers:
            return "No recent relevant research papers found."

        paper_summary = "\n".join([
            f"- {p['title']} by {', '.join(p['authors'][:2])} - {p['url']}"
            for p in papers[:5]
        ])

        prompt = f"""
Summarize the latest ML research papers relevant to Kaggle competitions:

Recent Papers:
{paper_summary}

Generate a summary covering:
- Key research themes and trends
- Potential applications to competitions
- Notable findings or innovations
- Keep it concise (2 paragraphs)
- Include hyperlinks: [Paper Title](URL)
"""

        return self._generate_with_retry(prompt)

    def generate_github_repos_summary(
        self,
        repos: List[Dict[str, Any]]
    ) -> str:
        """Generate GitHub repositories summary.

        Args:
            repos: List of repository dictionaries

        Returns:
            Generated summary text
        """
        logger.info("Generating GitHub repositories summary...")

        if not repos:
            return "No relevant GitHub repositories found."

        repo_summary = "\n".join([
            f"- [{r['name']}]({r['url']}) - {r['description']} ({r['stars']} stars)"
            for r in repos[:5]
        ])

        prompt = f"""
Summarize the relevant GitHub repositories for Kaggle competitions:

Repositories:
{repo_summary}

Generate a summary covering:
- Overview of available resources
- Notable implementations or solutions
- Language and framework trends
- Keep it concise (1-2 paragraphs)
- Preserve the hyperlink format
"""

        return self._generate_with_retry(prompt)

    def predict_trends(
        self,
        competitions: List[Dict[str, Any]],
        historical_data: Dict[str, Any] = None
    ) -> str:
        """Predict leaderboard and algorithm trends.

        Args:
            competitions: List of competition dictionaries
            historical_data: Optional historical data

        Returns:
            Generated predictions text
        """
        logger.info("Generating trend predictions...")

        comp_types = [comp.get('category', 'Unknown') for comp in competitions]
        complexity_levels = [comp.get('complexity_level', 'Unknown') for comp in competitions]

        prompt = f"""
As a data science research engineer, predict upcoming trends in Kaggle competitions based on current data.

Current Competition Landscape:
- Categories: {', '.join(set(comp_types))}
- Complexity Levels: {', '.join(set(complexity_levels))}
- Total Active Competitions: {len(competitions)}

Generate predictions covering:
- Algorithm trends likely to dominate
- Expected leaderboard movements and patterns
- Emerging techniques or approaches
- Competition category trends
- Keep it analytical and data-driven (2-3 paragraphs)
"""

        return self._generate_with_retry(prompt)

    def _format_leaderboard(self, teams: List[Dict[str, Any]]) -> str:
        """Format leaderboard data for prompt.

        Args:
            teams: List of team dictionaries

        Returns:
            Formatted string
        """
        if not teams:
            return "No leaderboard data available"

        return "\n".join([
            f"{i+1}. {team.get('teamName', 'Unknown')} - Score: {team.get('score', 'N/A')}"
            for i, team in enumerate(teams)
        ])

    def _generate_with_retry(self, prompt: str) -> str:
        """Generate content with retry logic and rate limit handling.

        Args:
            prompt: Generation prompt

        Returns:
            Generated text
        """
        max_retries = self.config.get('gemini.retry_attempts', 3)
        retry_delay = self.config.get('gemini.retry_delay', 15)  # Default 15s for rate limits

        # Rate limit tracking
        rate_limit_delay = self.config.get('gemini.rate_limit_delay', 15)  # 15s between calls = 4 calls/minute (under 5/min limit)

        last_error = None
        for attempt in range(max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{max_retries} for content generation")

                # Enforce rate limiting: ensure minimum delay between API calls
                # Free tier: 5 requests per minute, so wait at least 15 seconds between calls
                current_time = time.time()
                time_since_last_request = current_time - self.last_request_time
                if self.last_request_time > 0 and time_since_last_request < rate_limit_delay:
                    wait_time = rate_limit_delay - time_since_last_request
                    logger.info(f"Rate limiting: waiting {wait_time:.1f}s before next API call")
                    time.sleep(wait_time)

                # Make the API call
                self.last_request_time = time.time()
                response = self.model.generate_content(prompt)

                # Check if response has text
                if hasattr(response, 'text') and response.text:
                    logger.debug(f"Content generated successfully on attempt {attempt + 1}")
                    return response.text
                elif hasattr(response, 'parts'):
                    # Handle response with parts
                    text = ''.join(part.text for part in response.parts if hasattr(part, 'text'))
                    if text:
                        logger.debug(f"Content generated from parts on attempt {attempt + 1}")
                        return text
                else:
                    logger.warning(f"Response has no text content on attempt {attempt + 1}")
                    last_error = "Response has no text content"

            except AttributeError as e:
                # Handle blocked content or missing text attribute
                logger.warning(f"Generation attempt {attempt + 1} - AttributeError (possibly blocked content): {e}")
                last_error = f"AttributeError: {str(e)}"

            except Exception as e:
                error_str = str(e)
                logger.warning(f"Generation attempt {attempt + 1} failed: {type(e).__name__}: {e}")
                last_error = f"{type(e).__name__}: {error_str}"

                # Check if it's a rate limit error (ResourceExhausted or 429)
                if 'ResourceExhausted' in str(type(e).__name__) or '429' in error_str or 'quota' in error_str.lower():
                    # Extract retry delay from error message if available
                    import re
                    retry_match = re.search(r'retry in (\d+\.?\d*)s', error_str)
                    if retry_match:
                        suggested_delay = float(retry_match.group(1))
                        logger.warning(f"Rate limit exceeded. API suggests waiting {suggested_delay}s")
                        # Wait the suggested time plus a buffer
                        sleep_time = suggested_delay + 5
                    else:
                        # Default: wait 60 seconds for rate limit reset
                        sleep_time = 60

                    logger.info(f"Rate limit hit. Waiting {sleep_time}s before retry...")
                    if attempt < max_retries - 1:
                        time.sleep(sleep_time)
                    continue

            if attempt < max_retries - 1:
                sleep_time = retry_delay * (attempt + 1)
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

        # All attempts failed
        logger.error(f"All {max_retries} generation attempts failed. Last error: {last_error}")
        return f"[Content generation failed after {max_retries} attempts. Error: {last_error}]"
