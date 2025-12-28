# Fix Kaggle Authentication in GitHub Actions

**Document Version:** 1.0
**Last Updated:** 2025-12-21 02:13 AM
**Status:** Action Required

---

## Problem

The blog generation workflow is failing with Kaggle 401 Unauthorized error:

```
2025-12-21 05:43:33 - kaggle_collector - ERROR - Error fetching competitions: (401)
Reason: Unauthorized
```

**Root Cause:** The GitHub Secrets `KAGGLE_USERNAME` and `KAGGLE_PASSWORD` contain invalid or expired credentials.

---

## Solution: Update GitHub Secrets with Valid Kaggle Credentials

### Step 1: Get Fresh Kaggle API Credentials

1. **Go to Kaggle Account Settings:**
   - Visit: https://www.kaggle.com/settings/account
   - Scroll down to the "API" section

2. **Generate New API Token:**
   - Click "Create New Token" button
   - This will download a `kaggle.json` file to your computer
   - **Important:** Save this file securely

3. **Open the kaggle.json file:**
   ```json
   {
     "username": "your_kaggle_username",
     "key": "abc123def456ghi789..."
   }
   ```

   You'll need both values from this file.

---

### Step 2: Update GitHub Repository Secrets

1. **Navigate to Repository Settings:**
   - Go to: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions

2. **Update KAGGLE_USERNAME:**
   - Find `KAGGLE_USERNAME` in the list
   - Click "Update"
   - Paste the `username` value from kaggle.json
   - Click "Update secret"

3. **Update KAGGLE_PASSWORD:**
   - Find `KAGGLE_PASSWORD` in the list
   - Click "Update"
   - Paste the `key` value from kaggle.json (the long alphanumeric string)
   - Click "Update secret"

---

### Step 3: Verify the Fix

**Option A: Manual Workflow Trigger**

1. Go to Actions tab: https://github.com/vivekgana/AI-daily-blogs/actions
2. Click "Generate Daily Kaggle Blog" workflow
3. Click "Run workflow" button
4. Click the green "Run workflow" button in the dropdown
5. Wait for the workflow to complete
6. Check logs - you should see successful Kaggle API calls

**Option B: Use Test Workflow**

1. Go to Actions: https://github.com/vivekgana/AI-daily-blogs/actions
2. Click "Run Tests On-Demand" workflow
3. Click "Run workflow"
4. Select "integration" from the test suite dropdown
5. Click "Run workflow"
6. This will test Kaggle connectivity without generating a full blog

---

## Current Workflow Configuration

The workflow expects these GitHub Secrets:

| Secret Name | Purpose | Where Used |
|------------|---------|------------|
| `KAGGLE_USERNAME` | Kaggle account username | generate-daily-blog.yml:34 |
| `KAGGLE_PASSWORD` | Kaggle API key | generate-daily-blog.yml:35 |
| `GEMINI_API_KEY` | Google Gemini API key | generate-daily-blog.yml:44 |
| `GITHUB_TOKEN` | Auto-provided by GitHub | generate-daily-blog.yml:45 |

**Note:** The secret is named `KAGGLE_PASSWORD` but it actually contains your Kaggle API **key** (not a password).

---

## Quick Test Scripts

We've provided two test scripts to verify your credentials work before updating GitHub Secrets:

### Option 1: Simple Quick Test
```bash
python test_kaggle_simple.py
```
Fast credential check with pass/fail output.

### Option 2: Comprehensive Test
```bash
python test_kaggle_auth.py
```
Detailed test with step-by-step verification, creates kaggle.json if needed, and tests API calls.

---

## Verify Credentials Locally (Manual Method)

If you want to test manually before updating GitHub Secrets:

### Windows (PowerShell):
```powershell
# Set environment variables
$env:KAGGLE_USERNAME = "your_username_here"
$env:KAGGLE_KEY = "your_api_key_here"
$env:GEMINI_API_KEY = "your_gemini_key_here"

# Create Kaggle config
mkdir -p $HOME\.kaggle
echo "{`"username`":`"$env:KAGGLE_USERNAME`",`"key`":`"$env:KAGGLE_KEY`"}" > $HOME\.kaggle\kaggle.json

# Run tests
pytest tests/integration/test_kaggle_integration.py -v
```

### Linux/macOS (Bash):
```bash
# Set environment variables
export KAGGLE_USERNAME="your_username_here"
export KAGGLE_KEY="your_api_key_here"
export GEMINI_API_KEY="your_gemini_key_here"

# Create Kaggle config
mkdir -p ~/.kaggle
echo "{\"username\":\"$KAGGLE_USERNAME\",\"key\":\"$KAGGLE_KEY\"}" > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json

# Run tests
pytest tests/integration/test_kaggle_integration.py -v
```

---

## Troubleshooting

### Error: "401 Unauthorized" persists after updating secrets

**Possible causes:**
1. **Incorrect username:** Make sure you copied the exact username from kaggle.json
2. **API key has spaces:** Ensure no leading/trailing spaces when pasting the key
3. **Old credentials cached:** GitHub Actions may cache secrets briefly
   - Solution: Wait 5 minutes and try again
   - Or: Make a small change to the workflow file and commit it

### Error: "API key not found"

**Solution:**
- You haven't created a Kaggle API token yet
- Follow Step 1 above to generate one

### Error: "Rate limit exceeded"

**Solution:**
- Kaggle API has rate limits
- Wait 1 hour and try again
- Consider reducing the frequency of workflow runs

---

## Security Best Practices

1. **Never commit kaggle.json to git:**
   - It's already in .gitignore
   - Always use GitHub Secrets for credentials

2. **Rotate API keys regularly:**
   - Generate new tokens every 3-6 months
   - Revoke old tokens after generating new ones

3. **Use separate tokens for different purposes:**
   - Consider having one token for local development
   - Another token for GitHub Actions

4. **Revoke compromised tokens immediately:**
   - If you accidentally expose a token, revoke it at:
     https://www.kaggle.com/settings/account

---

## Expected Behavior After Fix

Once credentials are updated correctly, you should see:

**In workflow logs:**
```
2025-12-21 05:43:33 - kaggle_collector - INFO - Kaggle API authenticated successfully
2025-12-21 05:43:34 - kaggle_collector - INFO - Fetching active competitions...
2025-12-21 05:43:35 - kaggle_collector - INFO - Found 150 competitions
2025-12-21 05:43:35 - kaggle_collector - INFO - Ranking competitions...
```

**Generated blog will include:**
- Top 10 Kaggle competitions
- Leaderboard data (if available)
- Competition kernels
- AI-generated analysis and insights

---

## Related Files

- [generate-daily-blog.yml](../.github/workflows/generate-daily-blog.yml) - Main blog generation workflow
- [run-tests.yml](../.github/workflows/run-tests.yml) - Test workflow with Kaggle integration tests
- [kaggle_collector.py](../src/collectors/kaggle_collector.py) - Kaggle API wrapper

---

## Next Steps

1. ✅ Update GitHub Secrets with valid Kaggle credentials (Steps 1-2 above)
2. ✅ Run workflow manually to verify (Step 3 above)
3. ✅ Check workflow logs for successful authentication
4. ✅ Verify blog generation completes successfully
5. ✅ Monitor daily automated runs

---

**Questions or Issues?**

If you continue to experience authentication errors after following this guide:
1. Check the workflow run logs for specific error messages
2. Verify the secret names match exactly (case-sensitive)
3. Try regenerating the Kaggle API token
4. Check if your Kaggle account is in good standing

---

**Last Updated:** 2025-12-21 02:13 AM
**Branch:** fix/gemini-api-and-kaggle-leaderboard
**Status:** Awaiting credential update
