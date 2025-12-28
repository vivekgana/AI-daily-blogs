# Test Connectivity Using GitHub Secrets

**Last Updated:** 2025-12-15
**Purpose:** Verify that GitHub Secrets are properly configured and test API connectivity locally

---

## Overview

This guide helps you:
1. ✅ Verify GitHub Secrets are configured in the repository
2. ✅ Test API connectivity using those secret values
3. ✅ Run blog generation locally with the same credentials as GitHub Actions

---

## Prerequisites

- GitHub CLI (`gh`) installed
- Python 3.11+ with dependencies installed
- Access to repository secrets

---

## Step 1: Authenticate GitHub CLI

**Run this command:**
```powershell
gh auth login --web
```

**Follow the prompts:**
1. Select "GitHub.com"
2. Select "HTTPS"
3. Select "Yes" to authenticate Git with GitHub credentials
4. Follow the browser link and enter the code
5. Authorize GitHub CLI

**Verify authentication:**
```powershell
gh auth status
```

**Expected output:**
```
github.com
  ✓ Logged in to github.com account your-username (oauth_token)
  ✓ Token: gho_************************************
```

---

## Step 2: Verify GitHub Secrets Are Configured

**Run the verification script:**
```powershell
.\verify_github_secrets.ps1
```

**Expected output:**
```
======================================================================
 GITHUB SECRETS STATUS
======================================================================

[FOUND] KAGGLE_USERNAME
        Last updated: 2025-12-15T09:30:00Z
[FOUND] KAGGLE_PASSWORD
        Last updated: 2025-12-15T09:30:00Z
[FOUND] GEMINI_API_KEY
        Last updated: 2025-12-15T09:30:00Z
[FOUND] MY_GITHUB_ACTION
        Last updated: 2025-12-15T09:30:00Z

======================================================================
 SUMMARY
======================================================================

[SUCCESS] All required secrets are configured!
```

**If secrets are missing:**
- Go to: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
- Add the missing secrets:
  - `KAGGLE_USERNAME` - Your Kaggle username
  - `KAGGLE_PASSWORD` - Your Kaggle API key
  - `GEMINI_API_KEY` - Your Gemini API key
  - `MY_GITHUB_ACTION` - GitHub token (optional)

---

## Step 3: Set Environment Variables for Local Testing

**Important:** GitHub CLI cannot retrieve secret **values** for security reasons. You need to set environment variables manually with your actual credentials.

### Option A: Use Interactive Script (Recommended)

```powershell
.\set_github_secrets_env.ps1
```

This will ask you for each credential and set environment variables.

### Option B: Set Manually

**Get your credentials:**

1. **Kaggle Credentials:**
   - Go to: https://www.kaggle.com/settings/account
   - Click "Create New Token"
   - Download `kaggle.json`
   - Open the file:
     ```json
     {
       "username": "your_username",
       "key": "abc123def456..."
     }
     ```

2. **Gemini API Key:**
   - Go to: https://makersuite.google.com/app/apikey
   - Click "Create API key"
   - Copy the key (starts with `AIza...`)

**Set environment variables:**

```powershell
# PowerShell
$env:KAGGLE_USERNAME = "your_username_from_kaggle_json"
$env:KAGGLE_PASSWORD = "your_key_from_kaggle_json"
$env:GEMINI_API_KEY = "your_gemini_api_key"
```

**Verify they are set:**
```powershell
echo $env:KAGGLE_USERNAME
echo $env:KAGGLE_PASSWORD
echo $env:GEMINI_API_KEY
```

---

## Step 4: Test API Connectivity

**Run the connectivity test:**
```bash
python test_with_github_secrets.py
```

**Expected output:**
```
======================================================================
 TEST API CONNECTIVITY USING GITHUB SECRETS
======================================================================

======================================================================
 STEP 1: Verify GitHub Secrets Configuration
======================================================================

Fetching secrets from GitHub repository...

GitHub Secrets Status:
----------------------------------------------------------------------
[FOUND] KAGGLE_USERNAME
        Last updated: 2025-12-15T09:30:00Z
[FOUND] KAGGLE_PASSWORD
        Last updated: 2025-12-15T09:30:00Z
[FOUND] GEMINI_API_KEY
        Last updated: 2025-12-15T09:30:00Z
----------------------------------------------------------------------

[SUCCESS] All required secrets are configured in GitHub!

======================================================================
 STEP 2: Check Local Environment Variables
======================================================================

[SUCCESS] KAGGLE_USERNAME: Set (length: 12)
[SUCCESS] KAGGLE_PASSWORD: Set (length: 40)
[SUCCESS] GEMINI_API_KEY: Set (length: 39)
[WARNING] GITHUB_TOKEN: Not set (optional)

[SUCCESS] All required environment variables are set!

======================================================================
 STEP 3: Test Kaggle API Connection
======================================================================

Testing Kaggle API...
[INFO] Kaggle credentials written to C:\Users\gekambaram\.kaggle\kaggle.json
[SUCCESS] Kaggle API authenticated
[SUCCESS] Retrieved 425 competitions

Sample competitions:
  1. Google - Identify Contrails to Reduce Global Warming
     Teams: 5234, Reward: $100,000
  2. LLM Prompt Recovery
     Teams: 1889, Reward: Kudos
  3. Meta KDD Cup 2025 - Recommender Systems
     Teams: 3456, Reward: $75,000

======================================================================
 STEP 4: Test Gemini API Connection
======================================================================

Testing Gemini API...
[SUCCESS] Gemini API configured
[SUCCESS] Gemini API response received
[INFO] Response: API connection successful!

======================================================================
 STEP 5: Test GitHub API Connection (Optional)
======================================================================

[SKIP] GitHub token not configured (optional)

======================================================================
 SUMMARY
======================================================================

[PASS] Kaggle API
[PASS] Gemini API
[PASS] GitHub API

[SUCCESS] All required API connections working!

You can now run:
  python test_blog_generation_local.py

Or run the full blog generation:
  python src/main.py
```

---

## Step 5: Run Blog Generation

Once API connectivity tests pass:

```bash
python test_blog_generation_local.py
```

**Or run the main script:**
```bash
python src/main.py
```

---

## Troubleshooting

### Error: "GitHub CLI not authenticated"

**Fix:**
```powershell
# Clear any existing GITHUB_TOKEN that might interfere
$env:GITHUB_TOKEN = $null

# Authenticate
gh auth login --web
```

### Error: "401 Unauthorized" (Kaggle)

**Problem:** Kaggle credentials are incorrect

**Fix:**
1. Download fresh `kaggle.json` from https://www.kaggle.com/settings/account
2. Use the exact values from that file:
   ```powershell
   $env:KAGGLE_USERNAME = "value_from_kaggle_json"
   $env:KAGGLE_PASSWORD = "key_value_from_kaggle_json"
   ```
3. Make sure these match what's in GitHub Secrets
4. Update GitHub Secret if needed:
   ```powershell
   gh secret set KAGGLE_USERNAME --body "your_username" --repo vivekgana/AI-daily-blogs
   gh secret set KAGGLE_PASSWORD --body "your_api_key" --repo vivekgana/AI-daily-blogs
   ```

### Error: "API key not valid" (Gemini)

**Problem:** Gemini API key is incorrect or expired

**Fix:**
1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Set environment variable:
   ```powershell
   $env:GEMINI_API_KEY = "your_new_api_key"
   ```
4. Update GitHub Secret:
   ```powershell
   gh secret set GEMINI_API_KEY --body "your_new_api_key" --repo vivekgana/AI-daily-blogs
   ```

### Error: "Environment variables not persisting"

**Problem:** Variables only last for current PowerShell session

**Fix:** Create a script to set all variables at once:

**set_my_env.ps1:**
```powershell
$env:KAGGLE_USERNAME = "your_username"
$env:KAGGLE_PASSWORD = "your_api_key"
$env:GEMINI_API_KEY = "your_gemini_key"
Write-Host "Environment variables set!"
```

Then run before testing:
```powershell
. .\set_my_env.ps1
python test_with_github_secrets.py
```

---

## Verify GitHub Actions Will Work

Once local tests pass, your GitHub Actions workflows should also work because they use the same secrets.

**Test via GitHub Actions:**

1. Go to: https://github.com/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml
2. Click "Run workflow"
3. Select test suite: `credentials`
4. Click "Run workflow"
5. Wait 30 seconds and check results

**Expected result:**
```
✅ GEMINI_API_KEY: Set (length: 39)
✅ KAGGLE_USERNAME: Set (length: 12)
✅ KAGGLE_PASSWORD: Set (length: 40)
✅ GITHUB_TOKEN: Set (length: 40)
```

---

## Summary Workflow

```
1. gh auth login --web              ← Authenticate GitHub CLI
2. .\verify_github_secrets.ps1      ← Verify secrets in GitHub
3. .\set_github_secrets_env.ps1     ← Set local environment variables
4. python test_with_github_secrets.py  ← Test API connections
5. python test_blog_generation_local.py ← Generate blog locally
```

---

## Key Points

✅ **GitHub Secrets** - Configured in repository settings (encrypted)
✅ **Environment Variables** - Set locally with same values for testing
✅ **GitHub CLI** - Used to verify secrets exist (cannot read values)
✅ **Local Testing** - Uses env vars to test before pushing to GitHub Actions
✅ **GitHub Actions** - Automatically uses secrets from repository

**Security Note:** Never commit actual credentials to `.env` file or code!

---

## Quick Links

- **Repository Secrets:** https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
- **Kaggle API Token:** https://www.kaggle.com/settings/account
- **Gemini API Key:** https://makersuite.google.com/app/apikey
- **GitHub Actions:** https://github.com/vivekgana/AI-daily-blogs/actions
- **Test Workflows:** https://github.com/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml

---

**Ready to test?** Start with Step 1! 🚀
