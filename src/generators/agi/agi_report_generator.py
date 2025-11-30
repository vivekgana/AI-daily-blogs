"""AGI Research Report Generator using Google Gemini AI."""
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import google.generativeai as genai

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader

logger = setup_logger("agi_report_generator")


class AGIResearchReportGenerator:
    """Generate comprehensive AGI/ASI research reports."""

    def __init__(self, config: ConfigLoader):
        """Initialize AGI report generator.

        Args:
            config: Configuration loader instance
        """
        self.config = config

        # Configure Gemini API
        api_key = config.get_env('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

        # Use Gemini 1.5 Flash for cost-effective generation
        model_name = config.get('gemini.model', 'gemini-1.5-flash')

        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"AGI Report Generator initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise

    def generate_daily_agi_report(
        self,
        papers: List[Dict[str, Any]],
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive daily AGI research report.

        Args:
            papers: List of AGI research papers
            date: Report date (defaults to today)

        Returns:
            Dictionary with report content and metadata
        """
        if date is None:
            date = datetime.now()

        logger.info(f"Generating AGI research report for {date.strftime('%Y-%m-%d')}")
        logger.info(f"Processing {len(papers)} papers")

        # Filter and prioritize papers
        high_priority_papers = [p for p in papers if p.get('priority') in ['critical', 'high']]
        breakthrough_papers = [p for p in papers if p.get('agi_indicator_score', 0) > 7.0]

        logger.info(f"High priority papers: {len(high_priority_papers)}")
        logger.info(f"Potential breakthroughs: {len(breakthrough_papers)}")

        # Generate report sections
        report = {
            'date': date.strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'total_papers': len(papers),
            'high_priority_count': len(high_priority_papers),
            'breakthrough_count': len(breakthrough_papers),
        }

        # Executive Summary
        logger.info("Generating executive summary...")
        report['executive_summary'] = self._generate_executive_summary(
            papers,
            high_priority_papers,
            breakthrough_papers
        )

        # Breakthrough Analysis
        if breakthrough_papers:
            logger.info("Generating breakthrough analysis...")
            report['breakthrough_analysis'] = self._generate_breakthrough_analysis(
                breakthrough_papers
            )
        else:
            report['breakthrough_analysis'] = "No significant breakthroughs detected today."

        # Trend Analysis
        logger.info("Generating trend analysis...")
        report['trend_analysis'] = self._generate_trend_analysis(papers)

        # Research Highlights
        logger.info("Generating research highlights...")
        report['research_highlights'] = self._generate_research_highlights(
            high_priority_papers[:10]
        )

        # Safety Concerns
        safety_papers = [p for p in papers if 'safety' in str(p.get('title', '')).lower()
                        or 'alignment' in str(p.get('title', '')).lower()]
        if safety_papers:
            logger.info("Generating safety analysis...")
            report['safety_analysis'] = self._generate_safety_analysis(safety_papers)
        else:
            report['safety_analysis'] = "No significant safety-related papers detected today."

        # Recommendations
        logger.info("Generating recommendations...")
        report['recommendations'] = self._generate_recommendations(
            papers,
            high_priority_papers,
            breakthrough_papers
        )

        logger.info("AGI report generation completed successfully")
        return report

    def _generate_executive_summary(
        self,
        all_papers: List[Dict],
        high_priority: List[Dict],
        breakthroughs: List[Dict]
    ) -> str:
        """Generate executive summary."""

        # Calculate statistics
        total_count = len(all_papers)
        avg_agi_score = sum(p.get('agi_indicator_score', 0) for p in all_papers) / max(total_count, 1)

        # Get top keywords
        all_keywords = []
        for paper in all_papers:
            all_keywords.extend(paper.get('agi_keyword_matches', []))

        from collections import Counter
        top_keywords = Counter(all_keywords).most_common(10)

        prompt = f"""
As an AGI research analyst, write a concise executive summary for today's AGI research landscape.

**Statistics:**
- Total papers collected: {total_count}
- High priority papers: {len(high_priority)}
- Potential breakthroughs: {len(breakthroughs)}
- Average AGI relevance score: {avg_agi_score:.2f}/10
- Top research themes: {', '.join([kw for kw, count in top_keywords[:5]])}

**High Priority Papers:**
{self._format_paper_list(high_priority[:5])}

Write a 2-3 paragraph executive summary covering:
1. Overall state of AGI research today
2. Key developments and significant papers
3. Notable patterns or trends observed

Keep it professional, data-driven, and actionable for senior researchers and decision-makers.
"""

        return self._generate_with_retry(prompt)

    def _generate_breakthrough_analysis(self, papers: List[Dict]) -> str:
        """Generate breakthrough analysis."""

        prompt = f"""
Analyze these potential breakthrough papers in AGI research:

{self._format_paper_list(papers[:5])}

For each significant paper, provide:
1. **What makes it a potential breakthrough** - Novel approach, significant advance, or paradigm shift
2. **Technical significance** - Impact on AGI capabilities or understanding
3. **Implications** - How this could accelerate or alter AGI development
4. **Concerns** - Any safety, ethical, or alignment considerations

Be rigorous in your analysis. Not everything claiming to be a breakthrough actually is.
Format as markdown with clear sections for each paper.
"""

        return self._generate_with_retry(prompt)

    def _generate_trend_analysis(self, papers: List[Dict]) -> str:
        """Generate trend analysis."""

        # Analyze keywords and topics
        from collections import Counter

        all_keywords = []
        categories = []

        for paper in papers:
            all_keywords.extend(paper.get('agi_keyword_matches', []))
            categories.extend(paper.get('categories', []))

        keyword_trends = Counter(all_keywords).most_common(15)
        category_trends = Counter(categories).most_common(10)

        prompt = f"""
Analyze trends in current AGI research based on this data:

**Keyword Frequency:**
{chr(10).join([f"- {kw}: {count} mentions" for kw, count in keyword_trends])}

**Research Categories:**
{chr(10).join([f"- {cat}: {count} papers" for cat, count in category_trends])}

**Papers analyzed:** {len(papers)}

Provide trend analysis covering:
1. **Emerging Topics** - What's gaining attention in the research community
2. **Dominant Themes** - Current focus areas in AGI research
3. **Shifts & Changes** - Notable changes from typical research patterns
4. **Future Directions** - Where the research seems to be heading

Be analytical and data-driven. Identify real patterns, not noise.
Format as markdown with clear sections.
"""

        return self._generate_with_retry(prompt)

    def _generate_research_highlights(self, papers: List[Dict]) -> str:
        """Generate research highlights."""

        if not papers:
            return "No high-priority papers to highlight today."

        prompt = f"""
Summarize today's most important AGI research papers:

{self._format_paper_list(papers)}

For each paper, provide:
- **One-sentence summary** of what it does
- **AGI relevance** - Why it matters for AGI development
- **Key takeaway** - Main insight or contribution

Keep each paper summary to 2-3 sentences. Be concise but informative.
Format as a numbered markdown list.
"""

        return self._generate_with_retry(prompt)

    def _generate_safety_analysis(self, papers: List[Dict]) -> str:
        """Generate safety and alignment analysis."""

        prompt = f"""
Analyze these AI safety and alignment papers:

{self._format_paper_list(papers[:5])}

Provide analysis covering:
1. **Safety Concerns Addressed** - What risks or challenges are being tackled
2. **Proposed Solutions** - Approaches and methodologies
3. **Effectiveness Assessment** - How promising are these solutions
4. **Gaps Identified** - What safety issues remain unaddressed

Focus on concrete technical content. Be balanced and objective.
Format as markdown with clear sections.
"""

        return self._generate_with_retry(prompt)

    def _generate_recommendations(
        self,
        all_papers: List[Dict],
        high_priority: List[Dict],
        breakthroughs: List[Dict]
    ) -> str:
        """Generate actionable recommendations."""

        prompt = f"""
Based on today's AGI research activity, provide strategic recommendations:

**Context:**
- Total papers: {len(all_papers)}
- High priority: {len(high_priority)}
- Breakthroughs: {len(breakthroughs)}

**Top Papers:**
{self._format_paper_list(high_priority[:3])}

Provide recommendations for:
1. **Research Teams** - Which papers deserve deep investigation
2. **Safety Researchers** - Papers requiring safety analysis
3. **Decision Makers** - Strategic implications and actions
4. **Monitoring** - Areas requiring continued attention

Be specific and actionable. Format as markdown with clear sections.
"""

        return self._generate_with_retry(prompt)

    def _format_paper_list(self, papers: List[Dict]) -> str:
        """Format papers for prompts."""
        if not papers:
            return "No papers to display."

        formatted = []
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown')
            authors = paper.get('authors', [])
            author_str = ', '.join(authors[:3])
            if len(authors) > 3:
                author_str += ' et al.'

            abstract = paper.get('abstract', '')[:200] + '...' if len(paper.get('abstract', '')) > 200 else paper.get('abstract', '')

            agi_score = paper.get('agi_indicator_score', 0)
            url = paper.get('url', '')

            formatted.append(
                f"{i}. **{title}**\n"
                f"   - Authors: {author_str}\n"
                f"   - AGI Relevance: {agi_score}/10\n"
                f"   - Abstract: {abstract}\n"
                f"   - URL: {url}\n"
            )

        return '\n'.join(formatted)

    def _generate_with_retry(self, prompt: str) -> str:
        """Generate content with retry logic."""
        max_retries = self.config.get('gemini.retry_attempts', 3)
        retry_delay = self.config.get('gemini.retry_delay', 2)

        for attempt in range(max_retries):
            try:
                generation_config = {
                    'temperature': self.config.get('gemini.temperature', 0.7),
                    'max_output_tokens': self.config.get('gemini.max_tokens', 8000),
                }

                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                if response and hasattr(response, 'text') and response.text:
                    return response.text
                else:
                    raise ValueError("Empty response from Gemini API")

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Generation attempt {attempt + 1}/{max_retries} failed: {error_msg}")

                if "API key" in error_msg or "authentication" in error_msg.lower():
                    logger.error("Authentication error - check GEMINI_API_KEY")
                    return "[Content generation failed: Authentication error]"

                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"All {max_retries} generation attempts failed")
                    return f"[Content generation failed: {error_msg}]"

        return "[Content generation failed]"

    def format_report_markdown(self, report: Dict[str, Any]) -> str:
        """Format report as markdown."""

        md = f"""# AGI Research Daily Report
**Date:** {report['date']}
**Generated:** {report['generated_at']}

---

## 📊 Executive Summary

{report.get('executive_summary', 'N/A')}

**Statistics:**
- Total Papers Analyzed: {report['total_papers']}
- High Priority Papers: {report['high_priority_count']}
- Potential Breakthroughs: {report['breakthrough_count']}

---

## 🚀 Breakthrough Analysis

{report.get('breakthrough_analysis', 'No breakthroughs detected.')}

---

## 📈 Trend Analysis

{report.get('trend_analysis', 'No trend analysis available.')}

---

## 🔬 Research Highlights

{report.get('research_highlights', 'No highlights available.')}

---

## ⚠️ Safety & Alignment

{report.get('safety_analysis', 'No safety analysis available.')}

---

## 💡 Recommendations

{report.get('recommendations', 'No recommendations available.')}

---

*Report generated automatically by AGI Research Tracking System*
"""
        return md
