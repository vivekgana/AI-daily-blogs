"""
arXiv Collector specialized for AGI/ASI research
"""

import arxiv
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AGIKeywords:
    """AGI/ASI related keywords for research collection"""

    CORE_AGI = [
        'artificial general intelligence',
        'agi',
        'general intelligence',
        'artificial superintelligence',
        'asi',
        'general purpose ai'
    ]

    CAPABILITIES = [
        'transfer learning',
        'meta-learning',
        'few-shot learning',
        'zero-shot learning',
        'continual learning',
        'lifelong learning',
        'multitask learning',
        'curriculum learning'
    ]

    REASONING = [
        'reasoning',
        'common sense reasoning',
        'causal reasoning',
        'abstract reasoning',
        'logical reasoning',
        'analogical reasoning'
    ]

    ARCHITECTURES = [
        'world models',
        'foundation models',
        'large language models',
        'multimodal models',
        'neuro-symbolic',
        'hybrid ai'
    ]

    ALIGNMENT_SAFETY = [
        'ai alignment',
        'value alignment',
        'ai safety',
        'interpretability',
        'explainable ai',
        'robustness',
        'adversarial robustness'
    ]

    EMERGENCE = [
        'emergent capabilities',
        'emergent behavior',
        'scaling laws',
        'in-context learning'
    ]

    @classmethod
    def get_all_keywords(cls) -> List[str]:
        """Get all AGI-related keywords"""
        return (
            cls.CORE_AGI +
            cls.CAPABILITIES +
            cls.REASONING +
            cls.ARCHITECTURES +
            cls.ALIGNMENT_SAFETY +
            cls.EMERGENCE
        )

    @classmethod
    def get_priority_keywords(cls) -> List[str]:
        """Get high-priority keywords for focused search"""
        return (
            cls.CORE_AGI +
            cls.REASONING[:3] +
            cls.ALIGNMENT_SAFETY[:5]
        )


class ArxivAGICollector:
    """
    Specialized arXiv collector for AGI/ASI research papers
    """

    # arXiv categories most relevant to AGI research
    RELEVANT_CATEGORIES = [
        'cs.AI',  # Artificial Intelligence
        'cs.LG',  # Machine Learning
        'cs.CL',  # Computation and Language
        'cs.CV',  # Computer Vision
        'cs.NE',  # Neural and Evolutionary Computing
        'cs.RO',  # Robotics
        'cs.MA',  # Multiagent Systems
        'stat.ML',  # Machine Learning (Statistics)
    ]

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the arXiv AGI collector

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.client = arxiv.Client()
        self.keywords = AGIKeywords()
        self.logger = logging.getLogger(__name__)

    async def collect(
        self,
        max_results: int = 100,
        days_back: int = 7,
        use_priority_keywords: bool = False
    ) -> List[Dict]:
        """
        Collect AGI-related papers from arXiv

        Args:
            max_results: Maximum number of papers to collect
            days_back: How many days back to search
            use_priority_keywords: Use only priority keywords

        Returns:
            List of paper dictionaries
        """
        keywords = (
            self.keywords.get_priority_keywords()
            if use_priority_keywords
            else self.keywords.get_all_keywords()
        )

        self.logger.info(
            f"Collecting arXiv papers with {len(keywords)} keywords, "
            f"{days_back} days back, max {max_results} results"
        )

        # Build search query
        keyword_query = ' OR '.join([f'all:"{kw}"' for kw in keywords])
        category_query = ' OR '.join([f'cat:{cat}' for cat in self.RELEVANT_CATEGORIES])

        query = f'({keyword_query}) AND ({category_query})'

        # Calculate date range
        from_date = datetime.now() - timedelta(days=days_back)

        try:
            # Perform search
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            papers = []
            for result in self.client.results(search):
                # Filter by date
                if result.published.replace(tzinfo=None) < from_date:
                    continue

                paper = self._process_paper(result)
                if paper:
                    papers.append(paper)

            self.logger.info(f"Collected {len(papers)} papers from arXiv")
            return papers

        except Exception as e:
            self.logger.error(f"Error collecting from arXiv: {e}")
            raise

    def _process_paper(self, result: arxiv.Result) -> Dict:
        """
        Process arXiv result into standardized paper format

        Args:
            result: arXiv search result

        Returns:
            Paper dictionary
        """
        try:
            # Extract paper ID
            paper_id = result.entry_id.split('/')[-1].replace('v', '')

            # Calculate AGI relevance indicators
            agi_indicators = self._calculate_agi_indicators(
                result.title,
                result.summary,
                result.categories
            )

            paper = {
                'paper_id': f'arxiv_{paper_id}',
                'source': 'arxiv',
                'title': result.title.strip(),
                'authors': [author.name for author in result.authors],
                'abstract': result.summary.strip().replace('\n', ' '),
                'published_date': result.published.isoformat(),
                'updated_date': result.updated.isoformat(),
                'categories': result.categories,
                'primary_category': result.primary_category,
                'url': result.entry_id,
                'pdf_url': result.pdf_url,
                'doi': result.doi,
                'journal_ref': result.journal_ref,
                'comment': result.comment,

                # Metadata for prioritization
                'collection_timestamp': datetime.utcnow().isoformat(),
                'agi_keyword_matches': agi_indicators['keyword_matches'],
                'agi_indicator_score': agi_indicators['score'],

                # Processing flags
                'analyzed': False,
                'priority': self._calculate_priority(result, agi_indicators)
            }

            return paper

        except Exception as e:
            self.logger.error(f"Error processing paper {result.entry_id}: {e}")
            return None

    def _calculate_agi_indicators(
        self,
        title: str,
        abstract: str,
        categories: List[str]
    ) -> Dict:
        """
        Calculate AGI relevance indicators for a paper

        Args:
            title: Paper title
            abstract: Paper abstract
            categories: arXiv categories

        Returns:
            Dictionary with AGI indicators
        """
        text = f"{title} {abstract}".lower()

        # Count keyword matches
        keyword_matches = []
        for keyword in self.keywords.get_all_keywords():
            if keyword.lower() in text:
                keyword_matches.append(keyword)

        # Calculate base score
        score = len(keyword_matches) * 0.1

        # Boost for core AGI keywords
        for core_keyword in self.keywords.CORE_AGI:
            if core_keyword.lower() in text:
                score += 0.5

        # Boost for alignment/safety keywords
        for safety_keyword in self.keywords.ALIGNMENT_SAFETY:
            if safety_keyword.lower() in text:
                score += 0.3

        # Boost for specific categories
        if 'cs.AI' in categories:
            score += 0.2

        # Cap at 10
        score = min(score, 10.0)

        return {
            'keyword_matches': keyword_matches,
            'score': round(score, 2),
            'match_count': len(keyword_matches)
        }

    def _calculate_priority(
        self,
        result: arxiv.Result,
        agi_indicators: Dict
    ) -> str:
        """
        Calculate collection priority for a paper

        Args:
            result: arXiv result
            agi_indicators: AGI indicator scores

        Returns:
            Priority level (critical, high, medium, low)
        """
        score = agi_indicators['score']
        matches = agi_indicators['match_count']

        # Critical: High AGI score and core keywords
        if score >= 7.0 or matches >= 10:
            return 'critical'

        # High: Good AGI score or many matches
        if score >= 5.0 or matches >= 5:
            return 'high'

        # Medium: Moderate AGI relevance
        if score >= 3.0 or matches >= 3:
            return 'medium'

        # Low: Minimal AGI relevance
        return 'low'

    async def collect_by_authors(
        self,
        authors: List[str],
        max_results_per_author: int = 20,
        days_back: int = 180
    ) -> List[Dict]:
        """
        Collect papers by specific researchers

        Args:
            authors: List of author names
            max_results_per_author: Max results per author
            days_back: How many days back to search

        Returns:
            List of paper dictionaries
        """
        all_papers = []

        for author in authors:
            try:
                query = f'au:"{author}"'

                search = arxiv.Search(
                    query=query,
                    max_results=max_results_per_author,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )

                author_papers = []
                from_date = datetime.now() - timedelta(days=days_back)

                for result in self.client.results(search):
                    if result.published.replace(tzinfo=None) >= from_date:
                        paper = self._process_paper(result)
                        if paper:
                            author_papers.append(paper)

                all_papers.extend(author_papers)
                self.logger.info(
                    f"Collected {len(author_papers)} papers from author: {author}"
                )

            except Exception as e:
                self.logger.error(f"Error collecting papers for author {author}: {e}")
                continue

        return all_papers

    async def collect_by_category(
        self,
        category: str,
        max_results: int = 50,
        days_back: int = 7
    ) -> List[Dict]:
        """
        Collect papers from a specific arXiv category

        Args:
            category: arXiv category (e.g., 'cs.AI')
            max_results: Maximum results
            days_back: How many days back to search

        Returns:
            List of paper dictionaries
        """
        try:
            query = f'cat:{category}'

            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            papers = []
            from_date = datetime.now() - timedelta(days=days_back)

            for result in self.client.results(search):
                if result.published.replace(tzinfo=None) >= from_date:
                    paper = self._process_paper(result)
                    if paper:
                        # Only include if it has AGI relevance
                        if paper['agi_indicator_score'] > 1.0:
                            papers.append(paper)

            self.logger.info(
                f"Collected {len(papers)} AGI-relevant papers from category {category}"
            )
            return papers

        except Exception as e:
            self.logger.error(f"Error collecting from category {category}: {e}")
            raise
