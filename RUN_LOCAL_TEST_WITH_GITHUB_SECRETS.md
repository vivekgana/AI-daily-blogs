# Run Local Tests Using GitHub Secrets Values

**Purpose:** Test blog generation locally using the same credentials configured in GitHub Secrets.

**Problem:** The `.env` file has placeholder values, but you want to use your actual GitHub Secrets values.

**Solution:** Set environment variables before running the test.

---

## Quick Start (Recommended)

### Step 1: Get Your Kaggle Credentials

1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New Token"
4. Download `kaggle.json` file
5. Open the file - it contains:
   ```json
   {
     "username": "your_actual_username",
     "key": "abc123def456..."
   }
   ```

### Step 2: Get Your Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy the key (starts with `AIza...`)

### Step 3: Set Environment Variables

**PowerShell:**
```powershell
# Set Kaggle credentials (from kaggle.json)
$env:KAGGLE_USERNAME = "your_actual_username"
$env:KAGGLE_KEY = "abc123def456..."

# Set Gemini API key
$env:GEMINI_API_KEY = "AIzaSy..."

# Optional: GitHub token (for GitHub API features)
$env:GITHUB_TOKEN = "ghp_..."
```

**Command Prompt (cmd):**
```cmd
set KAGGLE_USERNAME=your_actual_username
set KAGGLE_KEY=abc123def456...
set GEMINI_API_KEY=AIzaSy...
set GITHUB_TOKEN=ghp_...
```

**Bash (Git Bash / WSL):**
```bash
export KAGGLE_USERNAME="your_actual_username"
export KAGGLE_KEY="abc123def456..."
export GEMINI_API_KEY="AIzaSy..."
export GITHUB_TOKEN="ghp_..."
```

### Step 4: Run the Test

```bash
python test_blog_generation_local.py
```

**Expected Output:**
```
======================================================================
 LOCAL BLOG GENERATION TEST
======================================================================
 Date: 2025-12-15 04:45:00
======================================================================

======================================================================
 TEST 1: Environment Setup
======================================================================
[PASS] .env file found
[PASS] Environment variables loaded

======================================================================
 TEST 2: API Credentials
======================================================================
[PASS] GEMINI_API_KEY: Set (length: 39)
[PASS] KAGGLE_USERNAME: Set (length: 12)
[PASS] KAGGLE_KEY: Set (length: 40)

======================================================================
 TEST 3: API Connections
======================================================================
[PASS] Gemini API: Connected
[PASS] Kaggle API: Connected (425 competitions)
[SKIP] GitHub API: No token configured (optional)

======================================================================
 TEST 4: Data Collectors
======================================================================
[PASS] Kaggle Collector: Retrieved 425 competitions
[PASS] Kaggle Ranking: Ranked 425 competitions
[PASS] GitHub Collector: Retrieved 5 repositories
[PASS] Research Collector: Retrieved 5 papers

======================================================================
 TEST 5: Blog Generation
======================================================================
[INFO] Generating blog... (this may take 30-60 seconds)
[PASS] Blog generation: Success
       Date: 2025-12-15
       Markdown: blogs/2025/12/15-kaggle-summary.md
       HTML: blogs/2025/12/15-kaggle-summary.html

======================================================================
 TEST 6: Output Validation
======================================================================
[PASS] Markdown file: blogs/2025/12/15-kaggle-summary.md
       Size: 45,678 bytes
[PASS] HTML file: blogs/2025/12/15-kaggle-summary.html
       Size: 52,341 bytes

======================================================================
 SUMMARY
======================================================================
[PASS] Environment
[PASS] Credentials
[PASS] API Connections
[PASS] Data Collectors
[PASS] Blog Generation
[PASS] Output Validation

Result: 6/6 steps passed

*** All tests passed!
    Blog generated successfully!
```

---

## Alternative: Use GitHub Secrets Directly (Advanced)

**Note:** GitHub doesn't allow direct access to secret values via CLI for security. You need to either:

1. **Use GitHub Actions** (recommended) - Secrets are automatically available
2. **Copy values manually** - Paste secret values into environment variables (shown above)
3. **Use a workflow to export secrets** - Create a temporary workflow that echoes secret values (not recommended for security)

### Why You Can't Read Secrets Directly

GitHub Secrets are encrypted and can only be accessed:
- By GitHub Actions workflows (automatically)
- By repository administrators via the web interface (masked)

You cannot retrieve secret values via GitHub CLI (`gh`) for security reasons.

---

## Verification Checklist

Before running tests, verify:

- [ ] Kaggle credentials downloaded from https://www.kaggle.com/settings/account
- [ ] Gemini API key obtained from https://makersuite.google.com/app/apikey
- [ ] Environment variables set in current shell session
- [ ] You're in the correct directory: `AI-daily-blogs`
- [ ] Python dependencies installed: `pip install -r requirements.txt`

---

## Troubleshooting

### Error: "401 Unauthorized" (Kaggle)

**Problem:** Kaggle credentials invalid or not set

**Fix:**
```powershell
# PowerShell: Check if variables are set
echo $env:KAGGLE_USERNAME
echo $env:KAGGLE_KEY

# If empty or wrong, set them again with correct values
$env:KAGGLE_USERNAME = "correct_username"
$env:KAGGLE_KEY = "correct_api_key"
```

### Error: "GEMINI_API_KEY not configured"

**Problem:** Gemini API key not set or invalid

**Fix:**
```powershell
# Set Gemini API key
$env:GEMINI_API_KEY = "AIzaSy..."

# Verify it's set
echo $env:GEMINI_API_KEY
```

### Error: Environment variables not persisting

**Problem:** Variables are only set for current session

**Fix:**
- Re-run the `$env:...` commands in each new PowerShell window
- OR: Create a script to set variables:

**set_env.ps1:**
```powershell
$env:KAGGLE_USERNAME = "your_username"
$env:KAGGLE_KEY = "your_api_key"
$env:GEMINI_API_KEY = "your_gemini_key"

Write-Host "[SUCCESS] Environment variables set"
Write-Host "Run: python test_blog_generation_local.py"
```

Then run:
```powershell
. .\set_env.ps1
python test_blog_generation_local.py
```

---

## Why Use Environment Variables?

1. **Same as GitHub Actions**: Your workflows use environment variables from secrets
2. **No .env file changes**: Keep `.env` with placeholders, don't commit real credentials
3. **Session-based**: Credentials only exist in current terminal session
4. **Secure**: No credential files that could be accidentally committed

---

## Updating GitHub Secrets

If your local credentials work but GitHub Actions fail, update secrets:

1. Go to: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
2. Update secrets:
   - `KAGGLE_USERNAME` → Your Kaggle username
   - `KAGGLE_PASSWORD` → Your Kaggle API key (from `kaggle.json`)
   - `GEMINI_API_KEY` → Your Gemini API key

**Note:** GitHub uses `KAGGLE_PASSWORD` for the API key, not `KAGGLE_KEY`.

---

## Summary

**To test locally with GitHub Secrets values:**

1. Download credentials from Kaggle and Gemini
2. Set environment variables in your shell
3. Run `python test_blog_generation_local.py`
4. Verify all tests pass
5. If tests pass locally, your GitHub Actions should also work (assuming secrets are configured correctly)

**Remember:** Environment variables only last for the current terminal session. Set them again if you open a new window.
