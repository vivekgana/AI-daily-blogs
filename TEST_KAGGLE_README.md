# Testing Kaggle Authentication

Quick guide to test your Kaggle credentials before updating GitHub Secrets.

---

## Two Test Scripts Available

### 🚀 Quick Test (Recommended for most users)

**File:** `test_kaggle_simple.py`

**What it does:**
- Fast credential check
- Simple pass/fail output
- Shows if authentication works

**Run it:**
```bash
python test_kaggle_simple.py
```

**Expected output if working:**
```
🔍 Testing Kaggle Authentication...

Username: your_username
API Key: abc1...xyz9

✅ Success! Found 150 competitions

Top 3 competitions:
  1. Machine Learning Competition
  2. Computer Vision Challenge
  3. NLP Tournament

✅ Authentication working!

You can now update GitHub Secrets with these credentials.
```

---

### 🔬 Comprehensive Test (For troubleshooting)

**File:** `test_kaggle_auth.py`

**What it does:**
- Step-by-step verification
- Checks environment variables
- Verifies kaggle.json file
- Creates kaggle.json if missing
- Tests API authentication
- Fetches sample competitions
- Provides detailed error messages

**Run it:**
```bash
python test_kaggle_auth.py
```

**Expected output:**
```
============================================================
Kaggle Authentication Test
============================================================

Step 1: Checking environment variables...
✅ KAGGLE_USERNAME: your_username
✅ KAGGLE_KEY: abc1****xyz9

Step 2: Checking kaggle.json file...
✅ Found kaggle.json at: /home/user/.kaggle/kaggle.json
   File permissions: 600

Step 3: Testing Kaggle API connection...
   Initializing Kaggle API...
   Authenticating...
✅ Authentication successful!

Step 4: Testing API call (fetching competitions)...
✅ Successfully fetched 150 competitions

   Sample competitions:
   1. Machine Learning Competition
      Category: Featured
      Reward: $50,000

   2. Computer Vision Challenge
      Category: Research
      Reward: $25,000

   3. NLP Tournament
      Category: Playground
      Reward: Knowledge

============================================================
✅ All tests passed!
============================================================

Your Kaggle credentials are working correctly.

Next steps:
1. Update GitHub Secrets with these credentials:
   - KAGGLE_USERNAME
   - KAGGLE_PASSWORD (use the API key)

2. Go to:
   https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions

3. Update the secrets and re-run the workflow
```

---

## Prerequisites

Before running the tests, you need to set up your Kaggle credentials:

### Step 1: Get Kaggle API Token

1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New Token"
4. Download the `kaggle.json` file

### Step 2: Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:KAGGLE_USERNAME = "your_username"
$env:KAGGLE_KEY = "your_api_key"
```

**Linux/macOS (Bash):**
```bash
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_api_key"
```

**Or place kaggle.json file at:**
- Windows: `C:\Users\YourName\.kaggle\kaggle.json`
- Linux/macOS: `~/.kaggle/kaggle.json`

---

## What to Do After Tests Pass

Once either test script passes:

1. **Note your credentials** (from the test output)
2. **Go to GitHub Secrets:**
   - Visit: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
3. **Update secrets:**
   - Update `KAGGLE_USERNAME` with your username
   - Update `KAGGLE_PASSWORD` with your API key (yes, it's called PASSWORD but contains the KEY)
4. **Test the workflow:**
   - Go to Actions tab
   - Click "Generate Daily Kaggle Blog"
   - Click "Run workflow"
   - Verify it completes successfully

---

## Troubleshooting

### Error: "Credentials not set"

**Solution:** Set environment variables or create kaggle.json file

### Error: "401 Unauthorized"

**Possible causes:**
- Wrong username or API key
- Leading/trailing spaces in credentials
- Expired API token

**Solution:**
1. Generate a fresh token from Kaggle
2. Copy credentials carefully
3. Re-run the test

### Error: "Network error" or "Connection refused"

**Possible causes:**
- No internet connection
- Firewall blocking Kaggle API
- Corporate proxy issues

**Solution:**
1. Check internet connection
2. Try from different network
3. Check firewall settings

### Error: "Rate limit exceeded"

**Solution:** Wait 1 hour and try again. Kaggle has API rate limits.

---

## Security Notes

⚠️ **Never commit credentials to git!**

- The test scripts only read credentials, never save them
- kaggle.json is in .gitignore
- Environment variables are temporary (session only)
- Always use GitHub Secrets for CI/CD

---

## Related Documentation

- [docs/FIX-KAGGLE-AUTHENTICATION.md](docs/FIX-KAGGLE-AUTHENTICATION.md) - Complete authentication guide
- [BRANCH_SUMMARY.md](BRANCH_SUMMARY.md) - Overview of all changes
- [docs/PARALLEL-TESTING.md](docs/PARALLEL-TESTING.md) - Parallel testing guide

---

**Questions?** See the comprehensive guide: [docs/FIX-KAGGLE-AUTHENTICATION.md](docs/FIX-KAGGLE-AUTHENTICATION.md)
