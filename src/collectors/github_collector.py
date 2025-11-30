"""GitHub repository collector."""
import os
from typing import List, Dict, Any
from github import Github, GithubException

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader


logger = setup_logger("github_collector")


class GitHubCollector:
    """Collect relevant GitHub repositories."""

    def __init__(self, config: ConfigLoader):
        """Initialize GitHub collector.

        Args:
            config: Configuration loader instance
        """
        self.config = config
        github_token = config.get_env('GITHUB_TOKEN')

        if github_token:
            self.github = Github(github_token)
            logger.info("GitHub API authenticated with token")
        else:
            self.github = Github()
            logger.warning("GitHub API initialized without token (rate limits apply)")

    def search_repositories_by_algorithms(
        self,
        competition_name: str,
        algorithms: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Search GitHub repositories by competition and algorithms.

        Args:
            competition_name: Name of the competition
            algorithms: List of algorithms to search for

        Returns:
            List of repository dictionaries
        """
        if algorithms is None:
            algorithms = self.config.get('github.search_algorithms', [])

        max_repos = self.config.get('github.max_repos_per_competition', 5)
        min_stars = self.config.get('github.min_stars', 10)

        logger.info(f"Searching repositories for {competition_name}...")

        all_repos = []
        seen_repos = set()

        # Search for each algorithm
        for algorithm in algorithms[:3]:  # Limit to avoid rate limits
            try:
                query = f"{competition_name} {algorithm} kaggle"
                logger.debug(f"Searching: {query}")

                repos = self.github.search_repositories(
                    query=query,
                    sort='stars',
                    order='desc'
                )

                # Get top results
                repo_count = 0
                for repo in repos:
                    if repo_count >= 5:  # Limit per algorithm
                        break

                    try:
                        if repo.full_name in seen_repos:
                            continue

                        stars = repo.stargazers_count if hasattr(repo, 'stargazers_count') else 0
                        if stars >= min_stars:
                            repo_dict = {
                                'name': repo.name if hasattr(repo, 'name') else 'Unknown',
                                'full_name': repo.full_name if hasattr(repo, 'full_name') else 'Unknown',
                                'url': repo.html_url if hasattr(repo, 'html_url') else '',
                                'description': repo.description if hasattr(repo, 'description') and repo.description else 'No description',
                                'stars': stars,
                                'language': repo.language if hasattr(repo, 'language') and repo.language else 'Unknown',
                                'updated_at': repo.updated_at.isoformat() if hasattr(repo, 'updated_at') and repo.updated_at else None,
                                'algorithm': algorithm
                            }
                            all_repos.append(repo_dict)
                            seen_repos.add(repo.full_name)
                            repo_count += 1

                            if len(all_repos) >= max_repos:
                                break
                    except Exception as repo_error:
                        logger.debug(f"Error processing repository: {repo_error}")
                        continue

            except GithubException as e:
                logger.warning(f"GitHub API error for '{algorithm}': {e.status if hasattr(e, 'status') else 'unknown'} - {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error searching for '{algorithm}': {type(e).__name__}: {e}")
                continue

            if len(all_repos) >= max_repos:
                break

        # Sort by stars
        if all_repos:
            all_repos.sort(key=lambda x: x.get('stars', 0), reverse=True)
            logger.info(f"Found {len(all_repos)} relevant repositories")
        else:
            logger.info(f"No repositories found for {competition_name}")

        return all_repos[:max_repos]

    def get_trending_ml_repos(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get trending machine learning repositories.

        Args:
            days: Number of days to look back

        Returns:
            List of trending repository dictionaries
        """
        logger.info("Fetching trending ML repositories...")

        try:
            # Search for recent ML repos
            query = "machine learning kaggle stars:>50"
            repos = self.github.search_repositories(
                query=query,
                sort='stars',
                order='desc'
            )

            trending = []
            for repo in repos[:10]:
                repo_dict = {
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'url': repo.html_url,
                    'description': repo.description or 'No description',
                    'stars': repo.stargazers_count,
                    'language': repo.language or 'Unknown',
                }
                trending.append(repo_dict)

            logger.info(f"Found {len(trending)} trending repositories")
            return trending

        except GithubException as e:
            logger.error(f"Error fetching trending repos: {e}")
            return []
