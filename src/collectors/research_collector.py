"""Research paper collector from arXiv and Papers with Code."""
import arxiv
from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader


logger = setup_logger("research_collector")


class ResearchCollector:
    """Collect research papers from various sources."""

    def __init__(self, config: ConfigLoader):
        """Initialize research collector.

        Args:
            config: Configuration loader instance
        """
        self.config = config
        self.arxiv_client = arxiv.Client()

    def search_arxiv_papers(
        self,
        query: str = "machine learning kaggle",
        max_results: int = 5,
        days_lookback: int = 30
    ) -> List[Dict[str, Any]]:
        """Search arXiv for relevant papers.

        Args:
            query: Search query
            max_results: Maximum number of papers
            days_lookback: Number of days to look back (default 30 for better coverage)

        Returns:
            List of paper dictionaries
        """
        logger.info(f"Searching arXiv for: {query} (last {days_lookback} days)")

        try:
            # Build search query
            search = arxiv.Search(
                query=query,
                max_results=max_results * 3,  # Get more to allow for filtering
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            papers = []
            cutoff_date = datetime.now() - timedelta(days=days_lookback)
            processed_count = 0

            for result in self.arxiv_client.results(search):
                processed_count += 1

                # Try to filter by date, but be flexible if date is missing
                try:
                    if hasattr(result, 'published') and result.published < cutoff_date:
                        continue
                except Exception as date_error:
                    logger.debug(f"Error checking paper date: {date_error}")
                    # Continue anyway if we can't check the date

                try:
                    paper_dict = {
                        'title': result.title if hasattr(result, 'title') else 'Untitled',
                        'authors': [author.name for author in result.authors] if hasattr(result, 'authors') else ['Unknown'],
                        'summary': result.summary[:500] if hasattr(result, 'summary') else 'No summary available',
                        'url': result.entry_id if hasattr(result, 'entry_id') else '',
                        'pdf_url': result.pdf_url if hasattr(result, 'pdf_url') else '',
                        'published': result.published.isoformat() if hasattr(result, 'published') else datetime.now().isoformat(),
                        'categories': result.categories if hasattr(result, 'categories') else [],
                        'primary_category': result.primary_category if hasattr(result, 'primary_category') else 'cs.LG'
                    }
                    papers.append(paper_dict)

                    if len(papers) >= max_results:
                        break
                except Exception as paper_error:
                    logger.debug(f"Error processing paper: {paper_error}")
                    continue

                # Prevent infinite loops
                if processed_count >= max_results * 5:
                    logger.warning(f"Processed {processed_count} papers, stopping search")
                    break

            logger.info(f"Found {len(papers)} papers on arXiv from last {days_lookback} days")
            return papers

        except Exception as e:
            logger.error(f"Error searching arXiv: {type(e).__name__}: {e}")
            return []

    def get_ml_papers_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get ML papers by specific topic.

        Args:
            topic: Research topic (e.g., 'computer vision', 'nlp')

        Returns:
            List of paper dictionaries
        """
        query = f"{topic} machine learning"
        days = self.config.get('research.days_lookback', 7)
        max_papers = self.config.get('research.max_papers', 5)

        return self.search_arxiv_papers(query, max_papers, days)

    def get_papers_for_competition(self, competition_title: str) -> List[Dict[str, Any]]:
        """Get relevant papers for a specific competition.

        Args:
            competition_title: Competition title

        Returns:
            List of paper dictionaries
        """
        logger.info(f"Searching papers for competition: {competition_title}")

        # Extract key terms from competition title
        keywords = self._extract_keywords(competition_title)
        query = " ".join(keywords[:3]) + " machine learning"

        days_lookback = self.config.get('research.days_lookback', 30)
        return self.search_arxiv_papers(query, max_results=3, days_lookback=days_lookback)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text.

        Args:
            text: Input text

        Returns:
            List of keywords
        """
        # Simple keyword extraction (could be improved with NLP)
        stopwords = {'a', 'an', 'the', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or', 'with'}

        words = text.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 3]

        return keywords

    def search_papers_with_code(self, query: str) -> List[Dict[str, Any]]:
        """Search Papers with Code for implementations.

        Args:
            query: Search query

        Returns:
            List of paper dictionaries with code
        """
        logger.info(f"Searching Papers with Code for: {query}")

        # Note: Papers with Code doesn't have an official API
        # This is a placeholder - you may need to use web scraping or find an unofficial API
        # For now, returning empty list

        logger.warning("Papers with Code integration not yet implemented")
        return []

    def get_latest_ml_research(self, max_papers: int = 5) -> List[Dict[str, Any]]:
        """Get latest ML research papers.

        Args:
            max_papers: Maximum number of papers

        Returns:
            List of paper dictionaries
        """
        categories = self.config.get('research.relevant_categories', ['cs.LG', 'cs.AI', 'cs.CV'])
        days_lookback = self.config.get('research.days_lookback', 30)

        logger.info(f"Fetching latest ML research from {len(categories)} categories")

        # Search across multiple categories
        all_papers = []

        for category in categories[:3]:  # Limit to top 3 categories
            query = f"cat:{category}"
            papers = self.search_arxiv_papers(query, max_results=3, days_lookback=days_lookback)
            all_papers.extend(papers)

            # Early exit if we have enough papers
            if len(all_papers) >= max_papers:
                break

        if not all_papers:
            # Fallback: try a broader search if category search fails
            logger.info("Category search yielded no results, trying broader search")
            all_papers = self.search_arxiv_papers(
                query="machine learning",
                max_results=max_papers,
                days_lookback=days_lookback * 2  # Double the lookback period
            )

        # Remove duplicates and sort by date
        unique_papers = {p['url']: p for p in all_papers}.values()
        sorted_papers = sorted(
            unique_papers,
            key=lambda x: x.get('published', ''),
            reverse=True
        )

        result = list(sorted_papers)[:max_papers]
        logger.info(f"Returning {len(result)} latest ML research papers")
        return result
