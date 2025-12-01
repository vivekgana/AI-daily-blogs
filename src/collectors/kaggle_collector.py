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

    def get_active_competitions(self) -> List[Dict[str, Any]]:
        """Get list of active competitions.

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
                    'tags': comp.tags if hasattr(comp, 'tags') else []
                }
                active_comps.append(comp_dict)

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
