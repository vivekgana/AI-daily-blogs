# CLAUDE.md - AI Assistant Guide for AI-daily-blogs

## Repository Overview

**Repository Name:** AI-daily-blogs
**Owner:** vivekgana
**Purpose:** A repository designed for creating and managing daily blog posts about AI topics, currently in early setup phase with automated notification infrastructure.

## Current State (as of 2025-11-26)

This is a fully-functional automated blog generation system containing:
- Complete Python codebase for Kaggle data collection and AI-powered blog generation
- GitHub Actions workflows for daily automation and GitHub Pages deployment
- Google Gemini AI integration for content generation
- Comprehensive error handling with retry logic and notifications
- Professional blog templates (Markdown and HTML)
- Production-ready configuration and documentation

## Repository Structure

```
AI-daily-blogs/
├── .github/
│   └── workflows/
│       ├── blank.yml                    # Legacy notification workflow
│       ├── generate-daily-blog.yml      # Main blog generation workflow
│       └── deploy-github-pages.yml      # GitHub Pages deployment
├── blogs/                               # Generated blog content (by date)
│   └── YYYY/MM/DD-kaggle-summary.{md,html}
├── config/
│   └── config.yaml                      # Main configuration file
├── src/
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── kaggle_collector.py          # Kaggle API integration
│   │   ├── github_collector.py          # GitHub repo discovery
│   │   └── research_collector.py        # arXiv paper fetching
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── gemini_generator.py          # Google Gemini AI integration
│   │   └── blog_generator.py            # Main blog orchestrator
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config_loader.py             # Configuration management
│   │   ├── logger.py                    # Logging utilities
│   │   └── error_handler.py             # Error handling & notifications
│   ├── __init__.py
│   └── main.py                          # Entry point
├── templates/
│   ├── blog_template.md                 # Markdown template
│   └── blog_template.html               # HTML template
├── logs/                                # Application logs (gitignored)
├── .gitignore                           # Git ignore rules
├── requirements.txt                     # Python dependencies
├── README.md                            # User documentation
└── CLAUDE.md                            # This file - AI assistant guide
```

## Implemented Workflows

### 1. Daily Blog Generation Workflow (`generate-daily-blog.yml`)

**Location:** `.github/workflows/generate-daily-blog.yml`

**Purpose:** Main workflow that generates daily Kaggle competition blog posts using AI.

**Trigger:**
- Scheduled: Daily at 7 AM EST (11:00 UTC) via cron
- Manual: Via `workflow_dispatch`

**Key Features:**
- Sets up Python 3.11 environment
- Installs all dependencies from requirements.txt
- Configures Kaggle API credentials
- Runs blog generation via `src/main.py`
- Commits and pushes generated blogs
- Error handling with retry logic
- Sends email notifications on failure
- Creates GitHub issues on failure
- Uploads error logs as artifacts

**Required Secrets:**
- `KAGGLE_USERNAME` - Kaggle username
- `KAGGLE_KEY` - Kaggle API key
- `GEMINI_API_KEY` - Google Gemini API key
- `GITHUB_TOKEN` - GitHub token (auto-provided)
- `EMAIL_USERNAME` - Gmail for notifications (optional)
- `EMAIL_PASSWORD` - Gmail app password (optional)
- `EMAIL_TO` - Notification recipient (optional)

**Outputs:**
- Markdown blog: `blogs/YYYY/MM/DD-kaggle-summary.md`
- HTML blog: `blogs/YYYY/MM/DD-kaggle-summary.html`
- Logs: Available as artifacts on failure

### 2. GitHub Pages Deployment (`deploy-github-pages.yml`)

**Location:** `.github/workflows/deploy-github-pages.yml`

**Purpose:** Deploys generated blogs to GitHub Pages for public access.

**Trigger:**
- Push to main/master branch with changes in `blogs/**`
- Manual: Via `workflow_dispatch`

**Key Features:**
- Generates index page for blog archive
- Copies all blog HTML files to _site
- Deploys to GitHub Pages
- Automatic page updates

**Permissions:**
- `contents: read`
- `pages: write`
- `id-token: write`

### 3. Test Notification Workflow (`blank.yml`)

**Location:** `.github/workflows/blank.yml`

**Purpose:** Sends automated email notifications for testing and monitoring.

**Trigger:**
- Scheduled: Every 5 minutes via cron (`*/5 * * * *`)
- Manual: Via `workflow_dispatch`

**Key Features:**
- Runs on Ubuntu latest
- Sends email via Gmail SMTP
- Includes workflow metadata in notifications
- Uses encrypted secrets for credentials

**Required Secrets:**
- `EMAIL_USERNAME` - Gmail account for sending
- `EMAIL_PASSWORD` - Gmail app password
- `EMAIL_TO` - Recipient email address

**Email Content Includes:**
- Repository information
- Branch and commit details
- Workflow run ID and timestamp
- Success status indicator

## Development Workflows

### Git Workflow

**Current Branch:** `claude/claude-md-migjjmstm4xqqfus-01DJXJZbrCUwPKTTTmaZ58pH`

**Branch Naming Convention:**
- Claude AI branches: `claude/claude-md-{identifier}-{session-id}`
- Feature branches: `feature/{feature-name}`
- Bug fixes: `fix/{issue-description}`
- Documentation: `docs/{doc-type}`

**Commit Message Convention:**
Follow conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `chore:` for maintenance tasks
- `workflow:` for GitHub Actions changes
- `test:` for test additions or modifications

### GitHub Actions Best Practices

1. **Workflow File Naming:**
   - Use descriptive names (avoid generic names like `blank.yml`)
   - Format: `{action}-{purpose}.yml` (e.g., `generate-daily-blog.yml`)

2. **Security:**
   - Always use secrets for credentials
   - Never commit sensitive information
   - Use least-privilege permissions

3. **Scheduling:**
   - Current workflow runs every 5 minutes (very frequent)
   - Consider reducing frequency for production workflows
   - Use `workflow_dispatch` for manual testing

## Key Conventions for AI Assistants

### When Working on This Repository

1. **Understanding the Purpose:**
   - This is an AI blog automation project
   - Focus on creating sustainable, automated content generation
   - Prioritize quality over quantity

2. **Code Organization:**
   - Keep workflows in `.github/workflows/`
   - Store blog content separately from code
   - Use date-based organization for blog posts
   - Maintain clear separation between templates and generated content

3. **Adding New Features:**
   - Read existing files before modifying
   - Update this CLAUDE.md when adding new workflows or structure
   - Test workflows locally when possible before committing
   - Document all new secrets required in this file

4. **Blog Content Guidelines:**
   - Focus on AI-related topics
   - Ensure content is accurate and well-researched
   - Include proper attribution for sources
   - Maintain consistent formatting

5. **Automation Principles:**
   - Make workflows idempotent (safe to run multiple times)
   - Include proper error handling
   - Log meaningful information
   - Add notifications for important events

### File Modification Guidelines

1. **Workflow Files:**
   - Always validate YAML syntax
   - Test with `workflow_dispatch` before scheduling
   - Document trigger conditions clearly
   - Include failure notifications

2. **Documentation:**
   - Update README.md for user-facing documentation
   - Update CLAUDE.md for AI assistant guidance
   - Keep both files synchronized
   - Use clear, concise language

3. **Configuration:**
   - Use environment variables for flexibility
   - Document all configuration options
   - Provide sensible defaults
   - Validate configuration on startup

### Secrets Management

**Current Secrets in Use:**
| Secret Name | Purpose | Format | Required |
|------------|---------|--------|----------|
| `KAGGLE_USERNAME` | Kaggle username | username | ✅ Yes |
| `KAGGLE_KEY` | Kaggle API key | 40-char hex string | ✅ Yes |
| `GEMINI_API_KEY` | Google Gemini AI | API key string | ✅ Yes |
| `GITHUB_TOKEN` | GitHub API access | Auto-provided or PAT | ⚠️ Optional |
| `EMAIL_USERNAME` | Gmail sending account | email@gmail.com | ⚠️ Optional |
| `EMAIL_PASSWORD` | Gmail app password | 16-char app password | ⚠️ Optional |
| `EMAIL_TO` | Notification recipient | email@example.com | ⚠️ Optional |

**How to Get Secrets:**
1. **Kaggle**: Visit kaggle.com/settings/account → API → Create New Token
2. **Gemini**: Visit makersuite.google.com/app/apikey → Create API key
3. **GitHub Token**: Settings → Developer settings → Personal access tokens
4. **Gmail**: Enable 2FA → App passwords → Generate new password

### Testing Strategy

1. **Workflow Testing:**
   - Use `workflow_dispatch` for manual testing
   - Test with dry-run options when available
   - Validate outputs before committing
   - Check logs for errors and warnings

2. **Content Testing:**
   - Review generated content for quality
   - Check formatting and links
   - Validate metadata
   - Ensure proper encoding

## Common Tasks and How to Approach Them

### Task: Add a New GitHub Actions Workflow

1. Research existing workflows in `.github/workflows/`
2. Create a new workflow file with descriptive name
3. Follow the structure of existing workflows
4. Add proper triggers and permissions
5. Document required secrets in this file
6. Test with `workflow_dispatch` first
7. Commit with clear message

### Task: Modify Notification Frequency

1. Open `.github/workflows/blank.yml`
2. Locate the `schedule` section (line 4-6)
3. Modify the cron expression
4. Common patterns:
   - Every hour: `0 * * * *`
   - Daily at 9 AM: `0 9 * * *`
   - Weekdays at 9 AM: `0 9 * * 1-5`
5. Commit changes with explanation

### Task: Add Blog Generation Logic

1. Decide on technology stack (Python, Node.js, etc.)
2. Create appropriate directory structure:
   - `src/` for source code
   - `templates/` for blog templates
   - `blogs/` for generated content
3. Add package manager files (package.json, requirements.txt)
4. Create GitHub Actions workflow for generation
5. Add documentation to README.md
6. Update this CLAUDE.md with new structure

### Task: Set Up Content Publishing

1. Choose publishing platform (GitHub Pages, Medium, etc.)
2. Create publishing workflow
3. Add necessary secrets for platform API
4. Test publishing in staging environment
5. Document the publishing process
6. Set up monitoring and error alerts

## System Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                       │
│                   (Daily at 7 AM EST / 11 UTC)                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       src/main.py                               │
│                  (Orchestrates execution)                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Kaggle     │  │   GitHub     │  │   arXiv      │
│  Collector   │  │  Collector   │  │  Collector   │
│              │  │              │  │              │
│ - Top 10     │  │ - Repos by   │  │ - ML papers  │
│   comps      │  │   algorithm  │  │ - Recent     │
│ - Leaderboard│  │ - Trending   │  │   research   │
│ - Kernels    │  │   repos      │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
              ┌──────────────────────┐
              │   BlogGenerator      │
              │  (Aggregates data)   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  GeminiGenerator     │
              │  (AI content gen)    │
              │                      │
              │ - Overview           │
              │ - Analysis           │
              │ - Summaries          │
              │ - Predictions        │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Jinja2 Templates   │
              │                      │
              │ - Markdown           │
              │ - HTML               │
              └──────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                                 ▼
┌──────────────┐                  ┌──────────────┐
│   .md file   │                  │  .html file  │
│  blogs/YYYY/ │                  │  blogs/YYYY/ │
│    MM/DD-... │                  │    MM/DD-... │
└──────┬───────┘                  └──────┬───────┘
       │                                 │
       └─────────────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Git Commit & Push  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   GitHub Pages       │
              │   (Public access)    │
              └──────────────────────┘
```

### Key Components

**1. Collectors (src/collectors/)**
- `kaggle_collector.py`: Fetches competition data, leaderboards, kernels
- `github_collector.py`: Searches repositories by algorithms
- `research_collector.py`: Retrieves papers from arXiv

**2. Generators (src/generators/)**
- `gemini_generator.py`: AI-powered content generation using Google Gemini
- `blog_generator.py`: Orchestrates data collection and content generation

**3. Utilities (src/utils/)**
- `config_loader.py`: Loads and manages YAML configuration
- `logger.py`: Sets up logging infrastructure
- `error_handler.py`: Handles errors, retries, and notifications

**4. Templates (templates/)**
- `blog_template.md`: Jinja2 template for Markdown output
- `blog_template.html`: Jinja2 template for HTML output

### Competition Ranking Algorithm

Competitions are scored using a weighted formula:

```python
score = (prize_normalized × 0.3) +
        (participants_normalized × 0.25) +
        (complexity_score × 0.25) +
        (industry_relevance × 0.2)
```

**Components:**
- **Prize**: Normalized to $100,000 cap
- **Participants**: Normalized to 5,000 teams cap
- **Complexity**: Based on keywords (multi-modal, time-series, NLP, CV, etc.)
- **Industry**: Based on sectors (healthcare, finance, retail, etc.)

## Dependencies and Tools

### Current Dependencies

**GitHub Actions:**
- `actions/checkout@v4` - Repository checkout
- `actions/setup-python@v4` - Python environment setup
- `dawidd6/action-send-mail@v3` - Email notifications
- `actions/github-script@v7` - GitHub API interactions
- `actions/upload-artifact@v3` - Error log uploads
- `actions/configure-pages@v4` - GitHub Pages setup
- `actions/upload-pages-artifact@v3` - Pages artifact upload
- `actions/deploy-pages@v4` - Pages deployment

**Python Dependencies:**

*Core:*
- `kaggle==1.6.6` - Kaggle API integration
- `requests==2.31.0` - HTTP requests
- `python-dotenv==1.0.0` - Environment variable management

*AI/ML:*
- `google-generativeai==0.3.2` - Google Gemini AI API

*Data Processing:*
- `pandas==2.1.4` - Data manipulation
- `numpy==1.26.2` - Numerical computing

*Web Scraping:*
- `beautifulsoup4==4.12.2` - HTML parsing
- `selenium==4.16.0` - Browser automation

*Research:*
- `arxiv==2.1.0` - arXiv paper API

*Templates & Rendering:*
- `jinja2==3.1.2` - Template engine

*GitHub Integration:*
- `PyGithub==2.1.1` - GitHub API wrapper

*Utilities:*
- `schedule==1.2.0` - Task scheduling
- `aiohttp==3.9.1` - Async HTTP
- `python-dateutil==2.8.2` - Date utilities
- `pytz==2023.3` - Timezone support

**External Services:**
- Kaggle API (www.kaggle.com/docs/api)
- Google Gemini AI (makersuite.google.com)
- GitHub API (api.github.com)
- arXiv API (arxiv.org/help/api)
- Gmail SMTP (smtp.gmail.com:587)

## Environment and Runtime

**GitHub Actions Environment:**
- OS: Ubuntu Latest
- Default shell: bash
- Timezone: UTC
- Execution context: GitHub-hosted runner

**Local Development:**
- Repository cloned to: `/home/user/AI-daily-blogs`
- Platform: Linux 4.4.0
- Git repository: Yes
- Current date: 2025-11-26

## Troubleshooting Guide

### Common Issues

**1. Workflow Not Triggering:**
- Check cron syntax validity
- Verify workflow file is on default branch
- Ensure repository has Actions enabled
- Check workflow permissions

**2. Email Notifications Failing:**
- Verify secrets are set correctly
- Check Gmail app password (not regular password)
- Ensure "Less secure apps" or app passwords enabled
- Review SMTP server and port settings

**3. Git Push Failures:**
- Ensure branch name starts with `claude/`
- Verify session ID matches branch suffix
- Check network connectivity
- Retry with exponential backoff

### Debugging Workflows

1. Check Actions tab in GitHub repository
2. Review workflow run logs
3. Look for error messages in job outputs
4. Verify all required secrets are set
5. Test locally with act (GitHub Actions local runner)

## Security Considerations

1. **Never Commit:**
   - API keys or passwords
   - Email credentials
   - Personal information
   - Private tokens

2. **Always Use:**
   - GitHub Secrets for sensitive data
   - Environment variables for configuration
   - Least-privilege access
   - Encrypted communication

3. **Regular Reviews:**
   - Audit workflow permissions
   - Review secret usage
   - Check for exposed credentials
   - Update dependencies

## Future Enhancements

### Planned Features (Inferred)

1. **Automated Blog Generation:**
   - AI-powered content creation
   - Topic research and selection
   - Multi-format output (Markdown, HTML)

2. **Content Management:**
   - Blog post storage and organization
   - Version control for content
   - Archive management

3. **Publishing Pipeline:**
   - Automated publishing to platforms
   - Social media integration
   - RSS feed generation

4. **Quality Assurance:**
   - Content review workflows
   - Automated testing
   - Link validation

5. **Analytics and Monitoring:**
   - Performance tracking
   - Error monitoring
   - Usage statistics

## Resources and References

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [YAML Syntax Guide](https://yaml.org/)
- [Cron Expression Generator](https://crontab.guru/)

### Tools
- [act - Run GitHub Actions locally](https://github.com/nektos/act)
- [actionlint - Workflow linter](https://github.com/rhysd/actionlint)

### Best Practices
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions Security](https://docs.github.com/actions/security-guides)

## Maintenance Notes

**Last Updated:** 2025-11-26
**Updated By:** Claude AI Assistant
**Repository State:** Production-ready, fully automated blog generation system

**Feature Branch:** `feature/kaggle-daily-blog-automation`

**System Status:**
- ✅ Data collection (Kaggle, GitHub, arXiv)
- ✅ AI content generation (Google Gemini)
- ✅ Blog templates (MD + HTML)
- ✅ Daily automation (GitHub Actions)
- ✅ Error handling & notifications
- ✅ GitHub Pages deployment
- ⚠️ Requires API keys to be configured in GitHub Secrets
- ⚠️ Needs merge to main branch for production use

**Change Log:**
- 2025-11-26 (Initial): Created CLAUDE.md with repository analysis
- 2025-11-26 (Update): Implemented complete Kaggle blog automation system:
  - Added Python codebase (collectors, generators, utilities)
  - Implemented Google Gemini AI integration
  - Created blog templates (Markdown + HTML)
  - Set up daily GitHub Actions workflow
  - Configured GitHub Pages deployment
  - Added comprehensive error handling
  - Created full documentation (README.md)
  - Updated CLAUDE.md with complete architecture

---

## Notes for AI Assistants

When working on this repository:

1. **Always start by reading this file** to understand current state
2. **Update this file** when making structural changes
3. **Follow the conventions** outlined above
4. **Test before committing** especially for workflows
5. **Document your changes** clearly in commit messages
6. **Ask for clarification** if the purpose of a task is unclear
7. **Maintain security** by never exposing secrets
8. **Think about scalability** when adding features
9. **Keep it simple** - avoid over-engineering
10. **Update timestamps** and change logs when modifying this file

This repository is in its early stages. Help build a robust, maintainable, and useful AI blog automation system!
