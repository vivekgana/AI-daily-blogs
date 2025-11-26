"""Main blog generator orchestrator."""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import json
from jinja2 import Environment, FileSystemLoader

from src.collectors.kaggle_collector import KaggleCollector
from src.collectors.github_collector import GitHubCollector
from src.collectors.research_collector import ResearchCollector
from src.generators.gemini_generator import GeminiGenerator
from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader


logger = setup_logger("blog_generator")


class BlogGenerator:
    """Orchestrate blog generation process."""

    def __init__(self, config: ConfigLoader):
        """Initialize blog generator.

        Args:
            config: Configuration loader instance
        """
        self.config = config

        # Initialize collectors
        self.kaggle_collector = KaggleCollector(config)
        self.github_collector = GitHubCollector(config)
        self.research_collector = ResearchCollector(config)

        # Initialize AI generator
        self.gemini_generator = GeminiGenerator(config)

        # Setup Jinja2 templates
        template_dir = Path(__file__).parent.parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

        logger.info("Blog generator initialized")

    def generate_daily_blog(self) -> Dict[str, str]:
        """Generate daily blog content.

        Returns:
            Dictionary with 'markdown' and 'html' content
        """
        logger.info("Starting daily blog generation...")

        # Collect data
        data = self._collect_all_data()

        # Generate content sections
        sections = self._generate_sections(data)

        # Render blog
        markdown_content = self._render_markdown(sections, data)
        html_content = self._render_html(sections, data)

        # Save blog
        file_paths = self._save_blog(markdown_content, html_content)

        logger.info(f"Blog generated successfully: {file_paths}")

        return {
            'markdown': markdown_content,
            'html': html_content,
            'paths': file_paths
        }

    def _collect_all_data(self) -> Dict[str, Any]:
        """Collect all required data.

        Returns:
            Dictionary with collected data
        """
        logger.info("Collecting data from all sources...")

        data = {
            'date': datetime.now(),
            'competitions': [],
            'new_competitions': [],
            'leaderboards': {},
            'kernels': {},
            'github_repos': [],
            'research_papers': [],
            'latest_ml_papers': []
        }

        # Get competitions
        all_comps = self.kaggle_collector.get_active_competitions()
        ranked_comps = self.kaggle_collector.rank_competitions(all_comps)
        data['competitions'] = ranked_comps[:10]

        # Get new competitions
        data['new_competitions'] = self.kaggle_collector.get_new_competitions(days=1)

        # Get leaderboards and kernels for top competitions
        for comp in data['competitions'][:5]:  # Limit to top 5 to avoid rate limits
            comp_id = comp['id']

            # Leaderboard
            leaderboard = self.kaggle_collector.get_competition_leaderboard(comp_id)
            if leaderboard is not None:
                data['leaderboards'][comp_id] = leaderboard

            # Kernels
            kernels = self.kaggle_collector.get_competition_kernels(comp_id, max_kernels=5)
            data['kernels'][comp_id] = kernels

        # Get GitHub repositories
        for comp in data['competitions'][:3]:  # Top 3 competitions
            repos = self.github_collector.search_repositories_by_algorithms(comp['title'])
            data['github_repos'].extend(repos)

        # Get research papers
        for comp in data['competitions'][:3]:
            papers = self.research_collector.get_papers_for_competition(comp['title'])
            data['research_papers'].extend(papers)

        # Get latest ML research
        data['latest_ml_papers'] = self.research_collector.get_latest_ml_research(max_papers=5)

        logger.info("Data collection completed")
        return data

    def _generate_sections(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate all blog sections using AI.

        Args:
            data: Collected data dictionary

        Returns:
            Dictionary with generated sections
        """
        logger.info("Generating content sections...")

        sections = {}

        # Competition Overview
        sections['overview'] = self.gemini_generator.generate_competition_overview(
            data['competitions']
        )

        # Leaderboard Highlights
        leaderboard_analyses = []
        for comp in data['competitions'][:3]:
            comp_id = comp['id']
            if comp_id in data['leaderboards']:
                analysis = self.gemini_generator.generate_leaderboard_analysis(
                    comp,
                    data['leaderboards'][comp_id]
                )
                leaderboard_analyses.append(f"**{comp['title']}:**\n{analysis}")

        sections['leaderboard'] = "\n\n".join(leaderboard_analyses) if leaderboard_analyses else "No leaderboard data available."

        # Algorithm Summaries
        algorithm_summaries = []
        for comp in data['competitions'][:3]:
            comp_id = comp['id']
            if comp_id in data['kernels'] and data['kernels'][comp_id]:
                summary = self.gemini_generator.generate_algorithm_summary(
                    comp,
                    data['kernels'][comp_id]
                )
                algorithm_summaries.append(f"**{comp['title']}:**\n{summary}")

        sections['algorithms'] = "\n\n".join(algorithm_summaries) if algorithm_summaries else "No algorithm data available."

        # Research Papers
        sections['research'] = self.gemini_generator.generate_research_summary(
            data['research_papers']
        )

        # GitHub Repositories
        sections['github'] = self.gemini_generator.generate_github_repos_summary(
            data['github_repos']
        )

        # New Competitions
        if data['new_competitions']:
            new_comp_list = "\n".join([
                f"- **{comp['title']}** - {comp.get('reward', 'N/A')} - [Link]({comp['url']})"
                for comp in data['new_competitions']
            ])
            sections['new_competitions'] = f"New competitions launched:\n{new_comp_list}"
        else:
            sections['new_competitions'] = "No new competitions launched in the last 24 hours."

        # Predicted Trends
        sections['trends'] = self.gemini_generator.predict_trends(
            data['competitions']
        )

        # Latest ML Research
        sections['ml_research'] = self.gemini_generator.generate_research_summary(
            data['latest_ml_papers']
        )

        logger.info("Content generation completed")
        return sections

    def _render_markdown(self, sections: Dict[str, str], data: Dict[str, Any]) -> str:
        """Render markdown blog.

        Args:
            sections: Generated sections
            data: Collected data

        Returns:
            Markdown content
        """
        template = self.jinja_env.get_template('blog_template.md')

        return template.render(
            date=data['date'],
            sections=sections,
            competitions=data['competitions'],
            github_repos=data['github_repos'],
            research_papers=data['research_papers']
        )

    def _render_html(self, sections: Dict[str, str], data: Dict[str, Any]) -> str:
        """Render HTML blog.

        Args:
            sections: Generated sections
            data: Collected data

        Returns:
            HTML content
        """
        template = self.jinja_env.get_template('blog_template.html')

        return template.render(
            date=data['date'],
            sections=sections,
            competitions=data['competitions'],
            github_repos=data['github_repos'],
            research_papers=data['research_papers']
        )

    def _save_blog(self, markdown: str, html: str) -> Dict[str, str]:
        """Save blog to files.

        Args:
            markdown: Markdown content
            html: HTML content

        Returns:
            Dictionary with file paths
        """
        now = datetime.now()

        # Create directory structure
        blog_dir = Path(self.config.get('blog.output_dir', 'blogs'))
        date_dir = blog_dir / str(now.year) / f"{now.month:02d}"
        date_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        base_name = f"{now.day:02d}-kaggle-summary"
        md_path = date_dir / f"{base_name}.md"
        html_path = date_dir / f"{base_name}.html"

        # Save files
        md_path.write_text(markdown, encoding='utf-8')
        html_path.write_text(html, encoding='utf-8')

        logger.info(f"Blog saved to {md_path} and {html_path}")

        return {
            'markdown': str(md_path),
            'html': str(html_path)
        }
