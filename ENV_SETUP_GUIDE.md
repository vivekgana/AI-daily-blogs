# Environment Setup Guide

**Last Updated:** 2025-12-28
**For:** Local development and testing

---

## Overview

This project now supports `.env` file for local development while GitHub Actions uses repository secrets. This provides a seamless development experience.

---

## How It Works

### Local Development
- Code automatically loads `.env` file from project root
- No need to manually set environment variables
- Works on Windows, Linux, and macOS

### GitHub Actions (CI/CD)
- Uses repository secrets (not .env file)
- .env file is in .gitignore (never committed)
- Secrets configured at: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions

---

## Current Status

### ⚠️ Your Kaggle Credentials Need Updating

I tested your current credentials from `.env` and they returned **401 Unauthorized**.

**This means:**
1. The API key may be expired or invalid
2. You need to generate a fresh token from Kaggle
3. The credentials need to be updated in both `.env` and GitHub Secrets

---

## Quick Fix: Update Kaggle Credentials

### Method 1: Automatic Setup (Recommended)

**Step 1:** Download fresh credentials
1. Go to: https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New Token"
4. Save the downloaded `kaggle.json` file

**Step 2:** Run the setup script
```bash
python setup_kaggle_credentials.py
```

This script will:
- Find your `kaggle.json` file
- Read the credentials
- Update your `.env` file
- Test the connection

---

### Method 2: Manual Setup

**Step 1:** Get credentials from kaggle.json

Open the downloaded `kaggle.json`:
```json
{
  "username": "your_username",
  "key": "your_api_key_here"
}
```

**Step 2:** Update .env file

Edit `.env` and update these lines:
```env
KAGGLE_USERNAME=your_username_from_kaggle_json
KAGGLE_KEY=your_api_key_from_kaggle_json
```

**Step 3:** Test the connection
```bash
python test_kaggle_simple.py
```

You should see:
```
✅ Loaded credentials from .env file
🔍 Testing Kaggle Authentication...
Username: your_username
API Key: abcd...xyz9
✅ Success! Found 150 competitions
```

---

## Testing Your Setup

### 1. Quick Test
```bash
python test_kaggle_simple.py
```

Fast credential check with simple pass/fail output.

### 2. Comprehensive Test
```bash
python test_kaggle_auth.py
```

Detailed test with step-by-step verification.

### 3. Run Unit Tests
```bash
pytest tests/unit/ -n 3 --dist loadfile -v
```

Runs all unit tests in parallel using your .env credentials.

### 4. Test Blog Generation
```bash
python src/main.py
```

Generates a full blog post using all APIs.

---

## Environment Variables in .env

Your `.env` file should contain:

```env
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Kaggle API
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key

# GitHub API (optional for local, required for CI)
GITHUB_TOKEN=your_github_token

# Email notifications (optional)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@email.com

# Development settings
ENVIRONMENT=development
DEBUG=true
```

---

## Troubleshooting

### Error: "401 Unauthorized" from Kaggle

**Problem:** Invalid or expired API credentials

**Solution:**
1. Generate fresh token: https://www.kaggle.com/settings/account
2. Click "Create New Token"
3. Run: `python setup_kaggle_credentials.py`
4. Or manually update `.env` file

---

### Error: ".env file not found"

**Problem:** .env file doesn't exist in project root

**Solution:**
Create `.env` file in project root:
```bash
# Windows PowerShell
New-Item -Path .env -ItemType File

# Linux/macOS
touch .env
```

Then add your credentials (see template above).

---

### Error: "Module 'dotenv' not found"

**Problem:** python-dotenv not installed

**Solution:**
```bash
pip install python-dotenv
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

---

### Test passes locally but fails in GitHub Actions

**Problem:** GitHub Secrets not updated

**Solution:**
1. Go to: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
2. Update these secrets:
   - `KAGGLE_USERNAME`
   - `KAGGLE_PASSWORD` (contains the API key)
   - `GEMINI_API_KEY`
3. Use the same values from your working `.env` file

---

## Security Best Practices

### ✅ Do's
- Keep `.env` file in .gitignore (already configured)
- Use different tokens for local and production if possible
- Rotate API keys regularly
- Use app passwords for Gmail (not your main password)

### ❌ Don'ts
- Never commit `.env` file to git
- Never share your API keys publicly
- Don't use production keys for local testing
- Don't disable .gitignore for .env

---

## What Changed

### Updated Files

1. **src/utils/config_loader.py**
   - Now automatically loads `.env` file if it exists
   - Transparent for local development
   - No changes needed for GitHub Actions

2. **test_kaggle_simple.py**
   - Loads credentials from `.env`
   - Fixed Windows Unicode issues
   - Better error messages

3. **test_kaggle_auth.py**
   - Enhanced with .env support
   - Comprehensive credential testing

4. **setup_kaggle_credentials.py** (NEW)
   - Auto-setup from kaggle.json
   - Updates .env file
   - Tests connection

---

## GitHub Actions Setup

GitHub Actions doesn't use `.env` file. It uses repository secrets.

### Update GitHub Secrets

**Navigate to:**
https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions

**Update these secrets with values from your working .env:**

| Secret Name | Value From | Example |
|------------|-----------|---------|
| `KAGGLE_USERNAME` | .env: KAGGLE_USERNAME | vivekgana |
| `KAGGLE_PASSWORD` | .env: KAGGLE_KEY | 9863daf... |
| `GEMINI_API_KEY` | .env: GEMINI_API_KEY | AIzaSy... |

**Note:** `KAGGLE_PASSWORD` in GitHub Secrets = `KAGGLE_KEY` in .env

---

## Next Steps

### Immediate Actions

1. **Generate fresh Kaggle credentials:**
   - Visit: https://www.kaggle.com/settings/account
   - Create new token

2. **Update local .env:**
   ```bash
   python setup_kaggle_credentials.py
   ```

3. **Test locally:**
   ```bash
   python test_kaggle_simple.py
   pytest tests/unit/ -v
   ```

4. **Update GitHub Secrets:**
   - Copy working credentials from .env
   - Update at: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions

5. **Test GitHub Actions:**
   - Go to Actions tab
   - Run "Generate Daily Kaggle Blog" workflow
   - Verify success

---

## Files Reference

- `.env` - Your local environment variables (in root directory)
- `.gitignore` - Ensures .env never gets committed
- `src/utils/config_loader.py` - Loads .env automatically
- `setup_kaggle_credentials.py` - Auto-setup helper
- `test_kaggle_simple.py` - Quick credential test
- `test_kaggle_auth.py` - Comprehensive test

---

## Support

If you continue having issues:

1. Check `.env` file exists in project root
2. Verify credentials are valid at Kaggle
3. Run: `python setup_kaggle_credentials.py`
4. Check GitHub Actions logs for specific errors

---

**Generated:** 2025-12-28
**Status:** Configuration complete, credentials need updating
**Branch:** fix/gemini-api-and-kaggle-leaderboard
