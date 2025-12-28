"""Kaggle competition data collector."""
import os
import json
from typing import List, Dict, Any, Optional
from kaggle.api.kaggle_api_extended import KaggleApi
from datetime import datetime, timedelta
import pandas as pd

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader


logger = setup_logger("kaggle_collector")


class KaggleCollector:
    """Collect data from Kaggle competitions."""

    def __init__(self, config: ConfigLoader):
        """Initialize Kaggle collector.

        Args:
            config: Configuration loader instance
        """
        self.config = config
        self.api = KaggleApi()
        self.api.authenticate()
        logger.info("Kaggle API authenticated successfully")

    def get_active_competitions(self, filter_featured=True) -> List[Dict[str, Any]]:
        """Get list of active competitions, optionally filtered for Featured competitions.

        Args:
            filter_featured: If True, only return Featured competitions

        Returns:
            List of competition dictionaries
        """
        logger.info("Fetching active competitions...")

        try:
            competitions = self.api.competitions_list()

            active_comps = []
            for comp in competitions:
                comp_dict = {
                    'id': comp.id,
                    'title': comp.title,
                    'url': comp.url,
                    'deadline': comp.deadline,
                    'category': comp.category,
                    'reward': comp.reward,
                    'teamCount': comp.teamCount,
                    'userHasEntered': comp.userHasEntered,
                    'description': comp.description if hasattr(comp, 'description') else '',
                    'tags': comp.tags if hasattr(comp, 'tags') else [],
                    'enabledDate': comp.enabledDate if hasattr(comp, 'enabledDate') else None,
                    'maxDailySubmissions': comp.maxDailySubmissions if hasattr(comp, 'maxDailySubmissions') else None,
                    'maxTeamSize': comp.maxTeamSize if hasattr(comp, 'maxTeamSize') else None,
                }

                # Filter for Featured competitions if requested
                if filter_featured:
                    # Featured competitions have category 'featured'
                    # Some competitions may have different categorization
                    category = str(comp.category).lower() if hasattr(comp, 'category') else ''

                    # Check if competition is featured
                    # Kaggle uses 'featured' category for official competitions
                    is_featured = (
                        'featured' in category or
                        category == 'featured' or
                        (hasattr(comp, 'isKernelsSubmissionsOnly') and not comp.isKernelsSubmissionsOnly)
                    )

                    if is_featured:
                        active_comps.append(comp_dict)
                        logger.debug(f"Featured competition found: {comp_dict['title']} (category: {category})")
                else:
                    active_comps.append(comp_dict)

            if filter_featured:
                logger.info(f"Found {len(active_comps)} Featured competitions out of {len(competitions)} total")
            else:
                logger.info(f"Found {len(active_comps)} active competitions")

            return active_comps

        except Exception as e:
            logger.error(f"Error fetching competitions: {e}")
            return []

    def rank_competitions(self, competitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank competitions based on configured criteria.

        Args:
            competitions: List of competition dictionaries

        Returns:
            Sorted list of competitions with scores
        """
        logger.info("Ranking competitions...")

        weights = self.config.get('competition_selection.ranking_weights', {})

        for comp in competitions:
            score = 0

            # Prize money score
            reward = comp.get('reward', '')
            prize_value = self._extract_prize_value(reward)
            prize_score = min(prize_value / 100000, 1.0) * weights.get('prize_money', 0.3)

            # Participants score
            team_count = comp.get('teamCount', 0)
            participant_score = min(team_count / 5000, 1.0) * weights.get('participants', 0.25)

            # Complexity score
            complexity_score = self._assess_complexity(comp) * weights.get('complexity', 0.25)

            # Industry relevance score
            industry_score = self._assess_industry_relevance(comp) * weights.get('industry_relevance', 0.2)

            # Total score
            comp['ranking_score'] = score + prize_score + participant_score + complexity_score + industry_score
            comp['prize_value'] = prize_value
            comp['complexity_level'] = self._get_complexity_level(comp)

        # Sort by score
        ranked = sorted(competitions, key=lambda x: x['ranking_score'], reverse=True)

        logger.info(f"Ranked {len(ranked)} competitions")
        return ranked

    def _extract_prize_value(self, reward: str) -> float:
        """Extract numeric prize value from reward string.

        Args:
            reward: Reward string (e.g., '$100,000')

        Returns:
            Numeric prize value
        """
        if not reward or reward == 'Kudos':
            return 0

        # Remove currency symbols and commas
        cleaned = reward.replace('$', '').replace(',', '').replace('USD', '').strip()

        try:
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0

    def _assess_complexity(self, comp: Dict[str, Any]) -> float:
        """Assess competition complexity.

        Args:
            comp: Competition dictionary

        Returns:
            Complexity score (0-1)
        """
        indicators = self.config.get('competition_selection.complexity_indicators', [])

        text = f"{comp.get('title', '')} {comp.get('description', '')}".lower()
        tags = [str(tag).lower() for tag in comp.get('tags', [])]

        matches = 0
        for indicator in indicators:
            if indicator.lower() in text or indicator.lower() in ' '.join(tags):
                matches += 1

        # Higher complexity = more indicators matched
        return min(matches / len(indicators), 1.0) if indicators else 0.5

    def _get_complexity_level(self, comp: Dict[str, Any]) -> str:
        """Get human-readable complexity level.

        Args:
            comp: Competition dictionary

        Returns:
            Complexity level string
        """
        score = self._assess_complexity(comp)

        if score >= 0.7:
            return "Very Complex"
        elif score >= 0.5:
            return "Complex"
        elif score >= 0.3:
            return "Moderate"
        else:
            return "Beginner-Friendly"

    def _assess_industry_relevance(self, comp: Dict[str, Any]) -> float:
        """Assess competition industry relevance.

        Args:
            comp: Competition dictionary

        Returns:
            Industry relevance score (0-1)
        """
        industries = self.config.get('competition_selection.industries', [])

        text = f"{comp.get('title', '')} {comp.get('description', '')}".lower()

        matches = 0
        for industry in industries:
            if industry.lower() in text:
                matches += 1

        return min(matches / len(industries), 1.0) if industries else 0.5

    def get_competition_leaderboard(self, competition_id: str) -> Optional[pd.DataFrame]:
        """Get competition leaderboard.

        Args:
            competition_id: Competition ID

        Returns:
            Leaderboard dataframe or None
        """
        try:
            logger.info(f"Fetching leaderboard for {competition_id}...")
            leaderboard = self.api.competition_leaderboard_view(competition_id)

            if leaderboard:
                entries = []
                for idx, entry in enumerate(leaderboard):
                    try:
                        # Extract fields with proper fallbacks
                        # Use actual rank if available, otherwise use index + 1
                        rank = getattr(entry, 'rank', idx + 1)
                        team_id = getattr(entry, 'teamId', 0)
                        team_name = getattr(entry, 'teamName', 'Unknown')
                        score = getattr(entry, 'score', 0.0)
                        submission_date = getattr(entry, 'submissionDate', None)

                        entries.append({
                            'rank': rank,
                            'teamId': team_id,
                            'teamName': team_name,
                            'score': score,
                            'submissionDate': submission_date
                        })
                    except Exception as entry_error:
                        logger.debug(f"Error processing leaderboard entry {idx}: {entry_error}")
                        continue

                if entries:
                    df = pd.DataFrame(entries)
                    logger.info(f"Successfully fetched {len(entries)} leaderboard entries for {competition_id}")
                    return df
                else:
                    logger.warning(f"No valid leaderboard entries found for {competition_id}")
                    return None
            else:
                logger.info(f"No leaderboard data available for {competition_id} (may be private or unavailable)")
                return None

        except Exception as e:
            logger.warning(f"Could not fetch leaderboard for {competition_id}: {type(e).__name__}: {e}")
            # Log more details for debugging
            import traceback
            logger.debug(f"Leaderboard fetch traceback: {traceback.format_exc()}")
            return None

    def get_competition_kernels(self, competition_id: str, max_kernels: int = 10) -> List[Dict[str, Any]]:
        """Get top kernels for a competition.

        Args:
            competition_id: Competition ID
            max_kernels: Maximum number of kernels to retrieve

        Returns:
            List of kernel dictionaries
        """
        try:
            logger.info(f"Fetching kernels for {competition_id}...")
            kernels = self.api.kernels_list(competition=competition_id, page_size=max_kernels, sort_by='voteCount')

            kernel_list = []
            for kernel in kernels[:max_kernels]:
                try:
                    kernel_dict = {
                        'title': kernel.title if hasattr(kernel, 'title') else 'Untitled',
                        'author': kernel.author if hasattr(kernel, 'author') else 'Unknown',
                        'url': f"https://www.kaggle.com{kernel.ref}" if hasattr(kernel, 'ref') else '',
                        'votes': kernel.voteCount if hasattr(kernel, 'voteCount') else 0,
                        'language': kernel.language if hasattr(kernel, 'language') else 'Unknown'
                    }
                    kernel_list.append(kernel_dict)
                except Exception as kernel_error:
                    logger.debug(f"Error processing kernel: {kernel_error}")
                    continue

            if kernel_list:
                logger.info(f"Found {len(kernel_list)} kernels for {competition_id}")
            else:
                logger.info(f"No kernels found for {competition_id} (may have no public kernels yet)")

            return kernel_list

        except Exception as e:
            logger.warning(f"Could not fetch kernels for {competition_id}: {type(e).__name__}: {e}")
            return []

    def get_daily_submission_stats(self, competition_id: str) -> Dict[str, Any]:
        """Get daily submission statistics for a competition.

        Args:
            competition_id: Competition ID

        Returns:
            Dictionary with submission statistics
        """
        try:
            logger.info(f"Fetching submission statistics for {competition_id}...")

            # Get competition details to find max daily submissions
            try:
                comp_list = self.api.competition_list_cli(competition=competition_id)
                comp_details = comp_list[0] if comp_list else None
            except:
                comp_details = None

            # Get leaderboard to analyze submission patterns
            leaderboard = self.get_competition_leaderboard(competition_id)

            stats = {
                'competition_id': competition_id,
                'max_daily_submissions': None,
                'total_submissions': 0,
                'unique_submitters': 0,
                'avg_submissions_per_team': 0,
                'submission_trend': 'unknown'
            }

            # Extract max daily submissions limit
            if comp_details and hasattr(comp_details, 'maxDailySubmissions'):
                stats['max_daily_submissions'] = comp_details.maxDailySubmissions
                logger.debug(f"Max daily submissions: {stats['max_daily_submissions']}")

            # Analyze leaderboard for submission patterns
            if leaderboard is not None and not leaderboard.empty:
                stats['unique_submitters'] = len(leaderboard)

                # If leaderboard has submission counts, calculate average
                if 'submissions' in leaderboard.columns:
                    stats['total_submissions'] = leaderboard['submissions'].sum()
                    stats['avg_submissions_per_team'] = leaderboard['submissions'].mean()

                logger.info(f"Submission stats: {stats['unique_submitters']} submitters")
            else:
                logger.info(f"No leaderboard data available for submission analysis")

            return stats

        except Exception as e:
            logger.warning(f"Error fetching submission stats for {competition_id}: {type(e).__name__}: {e}")
            return {
                'competition_id': competition_id,
                'max_daily_submissions': None,
                'total_submissions': 0,
                'unique_submitters': 0,
                'avg_submissions_per_team': 0,
                'submission_trend': 'error'
            }

    def get_algorithms_from_submissions(self, competition_id: str, max_kernels: int = 20) -> List[str]:
        """Extract algorithms from recent submission kernels when leaderboard is unavailable.

        Args:
            competition_id: Competition ID
            max_kernels: Maximum number of kernels to analyze

        Returns:
            List of detected algorithm names
        """
        try:
            logger.info(f"Extracting algorithms from submissions for {competition_id}...")

            # Get recent kernels (notebooks/scripts)
            kernels = self.get_competition_kernels(competition_id, max_kernels)

            if not kernels:
                logger.info(f"No kernels available for algorithm extraction: {competition_id}")
                return []

            # Common ML/AI algorithm keywords to detect
            algorithm_patterns = {
                # Deep Learning
                'transformer', 'bert', 'gpt', 'llm', 'large language model',
                'attention mechanism', 'self-attention', 'multi-head attention',
                'vision transformer', 'vit', 'clip', 'dall-e', 'stable diffusion',

                # Neural Networks
                'neural network', 'deep learning', 'cnn', 'convolutional',
                'rnn', 'lstm', 'gru', 'recurrent', 'autoencoder', 'gan',
                'resnet', 'efficientnet', 'mobilenet', 'densenet',

                # Ensemble Methods
                'xgboost', 'lightgbm', 'catboost', 'gradient boosting',
                'random forest', 'ensemble', 'stacking', 'blending',
                'bagging', 'boosting', 'adaboost',

                # Reinforcement Learning
                'reinforcement learning', 'q-learning', 'dqn', 'policy gradient',
                'actor-critic', 'ppo', 'a3c', 'ddpg', 'sac',

                # Meta-Learning
                'meta-learning', 'few-shot', 'zero-shot', 'one-shot',
                'transfer learning', 'fine-tuning', 'prompt engineering',
                'in-context learning', 'chain of thought',

                # Classic ML
                'svm', 'support vector', 'decision tree', 'knn',
                'k-means', 'naive bayes', 'logistic regression',
                'linear regression', 'ridge', 'lasso',

                # Other Advanced
                'neural architecture search', 'nas', 'automl',
                'multi-modal', 'multimodal', 'contrastive learning',
                'self-supervised', 'semi-supervised', 'active learning'
            }

            detected_algorithms = set()

            for kernel in kernels:
                # Search in title for algorithm mentions
                title = kernel.get('title', '').lower()
                for pattern in algorithm_patterns:
                    if pattern in title:
                        detected_algorithms.add(pattern.title())
                        logger.debug(f"Found algorithm '{pattern}' in kernel: {kernel.get('title')}")

            algorithms_list = sorted(list(detected_algorithms))

            if algorithms_list:
                logger.info(f"Detected {len(algorithms_list)} algorithms from {len(kernels)} kernels: {', '.join(algorithms_list[:5])}...")
            else:
                logger.info(f"No algorithms detected from kernel titles for {competition_id}")

            return algorithms_list

        except Exception as e:
            logger.warning(f"Error extracting algorithms from submissions: {type(e).__name__}: {e}")
            return []

    def get_new_competitions(self, days: int = 1) -> List[Dict[str, Any]]:
        """Get competitions launched in the last N days.

        Args:
            days: Number of days to look back

        Returns:
            List of new competition dictionaries
        """
        logger.info(f"Fetching competitions from last {days} days...")

        all_comps = self.get_active_competitions()
        cutoff_date = datetime.now() - timedelta(days=days)

        # Note: Kaggle API doesn't provide creation date easily
        # This is a simplified version - you may need to track this separately
        new_comps = []
        for comp in all_comps:
            # Heuristic: low team count might indicate newer competition
            if comp.get('teamCount', 0) < 100:
                new_comps.append(comp)

        logger.info(f"Found {len(new_comps)} potentially new competitions")
        return new_comps[:5]  # Return top 5
