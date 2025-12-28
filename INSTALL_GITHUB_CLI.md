# Install GitHub CLI Manually

The automatic installation failed due to permissions. Here's how to install manually:

## Option 1: Download Installer (Easiest)

1. Download the latest release:
   **Direct Download:** https://github.com/cli/cli/releases/latest/download/gh_windows_amd64.msi

2. Run the MSI installer
3. Follow the installation wizard
4. Restart your terminal/IDE

## Option 2: Use PowerShell (Admin Required)

Run PowerShell as Administrator and execute:
```powershell
winget install --id GitHub.cli
```

## Option 3: Use Scoop

```powershell
scoop install gh
```

## Verify Installation

After installing, restart your terminal and run:
```bash
gh --version
```

## Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to authenticate via browser.

## Create PR After Installation

```bash
cd c:\Users\gekambaram\source\personal\AI-daily-blogs
gh pr create \
  --title "Fix: Gemini API 404 error and Kaggle leaderboard rank bug + comprehensive testing" \
  --body-file .github/PR_DESCRIPTION.md \
  --base main \
  --head fix/gemini-api-and-kaggle-leaderboard
```

---

**Note:** You can also create the PR via the web interface using the link in CREATE_PR.md
