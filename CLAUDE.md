# CLAUDE.md - AI Assistant Guide for AI-daily-blogs

## Repository Overview

**Repository Name:** AI-daily-blogs
**Owner:** vivekgana
**Purpose:** A repository designed for creating and managing daily blog posts about AI topics, currently in early setup phase with automated notification infrastructure.

## Current State (as of 2025-11-26)

This is a minimal repository currently containing:
- GitHub Actions workflow for scheduled notifications
- No source code or blog content yet
- Foundation for future AI blog automation

## Repository Structure

```
AI-daily-blogs/
├── .github/
│   └── workflows/
│       └── blank.yml          # Scheduled notification workflow
├── .git/                      # Git repository data
└── CLAUDE.md                  # This file - AI assistant guide
```

### Expected Future Structure

Based on the repository name, the following structure is anticipated:

```
AI-daily-blogs/
├── .github/
│   └── workflows/
│       ├── blank.yml          # Current notification workflow
│       ├── generate-blog.yml  # Future: AI blog generation workflow
│       └── publish.yml        # Future: Blog publishing workflow
├── blogs/                     # Future: Generated blog posts
│   ├── YYYY-MM-DD/           # Date-based organization
│   └── archives/
├── templates/                 # Future: Blog templates
├── scripts/                   # Future: Automation scripts
├── src/                       # Future: Source code for blog generation
├── config/                    # Future: Configuration files
├── README.md                  # Future: Project documentation
├── package.json              # Future: If using Node.js
└── CLAUDE.md                 # This file
```

## Existing Workflows

### 1. Test Notification Workflow (`blank.yml`)

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
| Secret Name | Purpose | Format |
|------------|---------|--------|
| `EMAIL_USERNAME` | Gmail sending account | email@gmail.com |
| `EMAIL_PASSWORD` | Gmail app password | 16-char app password |
| `EMAIL_TO` | Notification recipient | email@example.com |

**Future Secrets Needed:**
- API keys for AI services (OpenAI, Anthropic, etc.)
- Database credentials (if using database)
- Publishing platform credentials
- Analytics tokens

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

## Dependencies and Tools

### Current Dependencies

**GitHub Actions:**
- `actions/checkout@v4` - Repository checkout
- `dawidd6/action-send-mail@v3` - Email notifications

**External Services:**
- Gmail SMTP (smtp.gmail.com:587)

### Recommended Future Dependencies

**For Blog Generation:**
- OpenAI API or Anthropic Claude API
- Markdown processors
- Template engines
- Content management tools

**For Publishing:**
- Static site generators (Hugo, Jekyll, Next.js)
- Publishing platform APIs
- RSS feed generators

**For Quality:**
- Linters and formatters
- Spell checkers
- Link validators
- Plagiarism checkers

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
**Repository State:** Initial setup phase

**Change Log:**
- 2025-11-26: Initial CLAUDE.md creation with repository analysis
- 2025-11-26: Added test notification workflow documentation

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
