# 📊 AI Daily Blogs - Kaggle Competition Tracker

Automated daily blog generation system that tracks top Kaggle competitions, analyzes algorithms, highlights research papers, and predicts ML trends.

## 🎯 Features

- **Top 10 Competition Tracking**: Automatically ranks competitions by prize money, participants, complexity, and industry relevance
- **Leaderboard Analysis**: Tracks and analyzes competition leaderboards daily
- **Algorithm Summaries**: Analyzes popular kernels and techniques being used
- **Research Paper Integration**: Fetches and summarizes relevant ML papers from arXiv
- **GitHub Repository Discovery**: Finds relevant repositories by algorithm
- **Trend Prediction**: AI-powered predictions of leaderboard movements and algorithm trends
- **Dual Format Output**: Generates both Markdown and HTML versions
- **Automated Publishing**: Daily execution via GitHub Actions at 7 AM EST
- **Error Handling**: Automatic retry, email notifications, and GitHub issue creation on failures

## 🏗️ Architecture

```
AI-daily-blogs/
├── .github/
│   └── workflows/
│       ├── generate-daily-blog.yml    # Main blog generation workflow
│       ├── deploy-github-pages.yml    # GitHub Pages deployment
│       └── blank.yml                  # Legacy notification workflow
├── blogs/                             # Generated blog content
│   └── YYYY/MM/DD-kaggle-summary.{md,html}
├── config/
│   └── config.yaml                    # Configuration settings
├── src/
│   ├── collectors/
│   │   ├── kaggle_collector.py       # Kaggle API integration
│   │   ├── github_collector.py       # GitHub repo discovery
│   │   └── research_collector.py     # arXiv paper fetching
│   ├── generators/
│   │   ├── gemini_generator.py       # Google Gemini AI integration
│   │   └── blog_generator.py         # Main orchestrator
│   ├── utils/
│   │   ├── config_loader.py          # Configuration management
│   │   ├── logger.py                 # Logging utilities
│   │   └── error_handler.py          # Error handling & notifications
│   └── main.py                        # Entry point
├── templates/
│   ├── blog_template.md              # Markdown template
│   └── blog_template.html            # HTML template
├── requirements.txt                   # Python dependencies
├── CLAUDE.md                         # AI assistant guide
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Kaggle API credentials
- Google Gemini API key
- GitHub token (optional, for higher rate limits)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/vivekgana/AI-daily-blogs.git
cd AI-daily-blogs
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file or set environment variables:

```bash
# Required
export KAGGLE_USERNAME="your_kaggle_username"
export KAGGLE_KEY="your_kaggle_api_key"
export GEMINI_API_KEY="your_gemini_api_key"

# Optional
export GITHUB_TOKEN="your_github_token"
export EMAIL_USERNAME="your_email@gmail.com"
export EMAIL_PASSWORD="your_gmail_app_password"
export EMAIL_TO="recipient@example.com"
```

4. **Run manually**
```bash
python src/main.py
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

- **Competition selection criteria**: Adjust ranking weights for prize money, participants, complexity, and industry relevance
- **GitHub search algorithms**: Specify which algorithms to search for
- **Research paper categories**: Choose arXiv categories to monitor
- **Blog sections**: Enable/disable specific sections
- **Gemini AI settings**: Adjust temperature, max tokens, retry logic
- **Error handling**: Configure retry attempts and notification preferences

## 🔐 GitHub Secrets

Set up the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description | Required |
|------------|-------------|----------|
| `KAGGLE_USERNAME` | Your Kaggle username | ✅ Yes |
| `KAGGLE_KEY` | Your Kaggle API key | ✅ Yes |
| `GEMINI_API_KEY` | Google Gemini API key | ✅ Yes |
| `GITHUB_TOKEN` | GitHub personal access token | ⚠️ Optional (for higher rate limits) |
| `EMAIL_USERNAME` | Gmail address for notifications | ⚠️ Optional (for error emails) |
| `EMAIL_PASSWORD` | Gmail app password | ⚠️ Optional (for error emails) |
| `EMAIL_TO` | Recipient email for notifications | ⚠️ Optional (for error emails) |

### Getting API Keys

**Kaggle API:**
1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New API Token"
4. Download `kaggle.json` and extract username and key

**Google Gemini API:**
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

**GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select `public_repo` scope
4. Copy the token

## 📅 Automation

The blog generates automatically every day at **7:00 AM EST** via GitHub Actions.

### Manual Trigger

You can manually trigger blog generation:

1. Go to Actions tab in GitHub
2. Select "Generate Daily Kaggle Blog" workflow
3. Click "Run workflow"

### Workflow Features

- ✅ Automatic blog generation
- ✅ Commits and pushes to repository
- ✅ Email notifications on failure
- ✅ GitHub issue creation on failure
- ✅ Error log artifacts
- ✅ Retry logic with exponential backoff

## 📖 Blog Structure

Each daily blog includes:

1. **Competition Overview**: Top 10 competitions with rankings
2. **Leaderboard Highlights**: Analysis of current standings
3. **Algorithm Summaries**: Popular techniques from public kernels
4. **Research Papers**: Relevant ML papers from arXiv
5. **GitHub Repositories**: Trending repos by algorithm
6. **New Competitions**: Recently launched competitions
7. **Predicted Trends**: AI-powered trend analysis
8. **Latest ML Research**: Cutting-edge ML research papers

## 🌐 GitHub Pages

Blogs are automatically published to GitHub Pages when pushed to the main branch.

### Enable GitHub Pages

1. Go to repository Settings
2. Navigate to Pages section
3. Set Source to "GitHub Actions"
4. Your blogs will be available at: `https://<username>.github.io/AI-daily-blogs/`

## 🛠️ Development

### Project Structure

- **Collectors**: Fetch data from various sources (Kaggle, GitHub, arXiv)
- **Generators**: Use AI to generate content sections
- **Templates**: Jinja2 templates for Markdown and HTML output
- **Utils**: Configuration, logging, and error handling

### Adding New Features

1. Create a new collector in `src/collectors/`
2. Add generation logic in `src/generators/`
3. Update templates in `templates/`
4. Modify `config.yaml` as needed
5. Update `CLAUDE.md` for AI assistants

### Testing

```bash
# Test blog generation locally
python src/main.py

# Check output
ls blogs/$(date +%Y)/%m/
```

## 🐛 Troubleshooting

### Common Issues

**Kaggle API Authentication Failed**
- Verify `KAGGLE_USERNAME` and `KAGGLE_KEY` are correct
- Ensure `~/.kaggle/kaggle.json` has proper permissions (600)

**Gemini API Quota Exceeded**
- Check your API quota at Google AI Studio
- Reduce generation frequency or content length

**GitHub Rate Limit**
- Add `GITHUB_TOKEN` secret for higher rate limits
- Reduce number of repository searches

**Blog Not Generated**
- Check GitHub Actions logs
- Verify all required secrets are set
- Look for error emails or GitHub issues

### Logs

Logs are stored in `logs/` directory and are available as artifacts in failed workflow runs.

## 📊 Ranking Algorithm

Competitions are ranked using a weighted scoring system:

```
Score = (Prize × 0.3) + (Participants × 0.25) + (Complexity × 0.25) + (Industry × 0.2)
```

- **Prize Money**: Normalized to $100,000
- **Participants**: Normalized to 5,000 teams
- **Complexity**: Based on keywords (multi-modal, time-series, NLP, CV, etc.)
- **Industry Relevance**: Based on industry keywords (healthcare, finance, etc.)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Kaggle** for providing competition data
- **Google Gemini** for AI content generation
- **arXiv** for research paper access
- **GitHub** for repository hosting and Actions

## 📧 Contact

For questions or issues, please:
- Open a GitHub issue
- Contact: vivekgana (repository owner)

---

**Powered by Google Gemini AI | Data from Kaggle, GitHub, and arXiv**

*Last updated: 2025-11-26*
