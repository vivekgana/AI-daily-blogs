# GitHub Secrets Setup Guide

**Document Version:** 1.0
**Last Updated:** 2025-11-30
**Purpose:** Configure GitHub Secrets for automated testing

## Overview

GitHub Secrets allow you to store sensitive credentials securely for use in GitHub Actions workflows. This guide shows how to configure all required secrets for running tests.

## Required Secrets

| Secret Name | Purpose | Required | Get From |
|-------------|---------|----------|----------|
| `GEMINI_API_KEY` | AI content generation | ✅ Yes | https://makersuite.google.com/app/apikey |
| `KAGGLE_USERNAME` | Competition data | ✅ Yes | https://www.kaggle.com/settings/account |
| `KAGGLE_KEY` | Competition data | ✅ Yes | https://www.kaggle.com/settings/account |
| `GH_TOKEN` | Repository search | ⚠️ Optional | https://github.com/settings/tokens |

## Step-by-Step Setup

### 1. Navigate to Repository Settings

1. Go to your repository: https://github.com/vivekgana/AI-daily-blogs
2. Click **Settings** (top menu)
3. In left sidebar, click **Secrets and variables** → **Actions**

### 2. Add Each Secret

Click **New repository secret** for each credential:

#### Secret 1: GEMINI_API_KEY

```
Name: GEMINI_API_KEY
Secret: AIzaSy...your_actual_gemini_key
```

**To get this key:**
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy`)
5. Paste into GitHub Secrets

#### Secret 2: KAGGLE_USERNAME

```
Name: KAGGLE_USERNAME
Secret: your_kaggle_username
```

**To get this:**
1. Visit: https://www.kaggle.com/settings/account
2. Your username is at the top
3. Or download kaggle.json and get "username" field

#### Secret 3: KAGGLE_KEY

```
Name: KAGGLE_KEY
Secret: your_40_character_kaggle_api_key
```

**To get this:**
1. Visit: https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New Token"
4. Download `kaggle.json`
5. Open it and copy the "key" value (40 characters)

#### Secret 4: GH_TOKEN (Optional but recommended)

```
Name: GH_TOKEN
Secret: ghp_...your_github_token
```

**To get this:**
1. Visit: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: "AI Daily Blogs Testing"
4. Expiration: 90 days (or custom)
5. Scopes: Check **`public_repo`** only
6. Click "Generate token"
7. **Copy immediately** (won't be shown again!)

### 3. Verify Secrets Are Set

After adding all secrets, you should see:

```
✅ GEMINI_API_KEY
✅ KAGGLE_USERNAME
✅ KAGGLE_KEY
✅ GH_TOKEN
```

**Important:** You won't be able to view the secret values again, only edit or delete them.

## Testing Your Secrets

### Method 1: Run Test Workflow Manually

1. Go to **Actions** tab
2. Select **"Test On-Demand"** workflow
3. Click **"Run workflow"**
4. Select test suite: **credentials**
5. Click **"Run workflow"**

This will verify all secrets are configured correctly.

### Method 2: Trigger Automated Test

Push any change to trigger the **"Run Tests"** workflow:

```bash
git commit --allow-empty -m "test: Verify GitHub Secrets"
git push origin main
```

Check the workflow run in the Actions tab.

## Workflow Files

### 1. Run Tests (Automatic)

**File:** `.github/workflows/run-tests.yml`

**Triggers:**
- Push to main/feature branches
- Pull requests
- Daily schedule (12 PM UTC)
- Manual dispatch

**Tests:**
- ✅ Unit tests (no credentials needed)
- ✅ Integration tests (uses secrets)
- ✅ Credential verification

### 2. Test On-Demand (Manual)

**File:** `.github/workflows/test-on-demand.yml`

**Trigger:** Manual only

**Options:**
- `all` - Run all tests
- `unit` - Unit tests only
- `integration` - Integration tests
- `kaggle` - Kaggle API tests
- `github` - GitHub API tests
- `research` - Research/arXiv tests
- `credentials` - Verify secrets

## Security Best Practices

### ✅ DO

- Use GitHub Secrets for all credentials
- Rotate secrets regularly (every 90 days)
- Use different keys for prod/test
- Limit token scopes to minimum needed
- Review secret access logs periodically

### ❌ DON'T

- Never log secret values in workflows
- Never commit secrets to repository
- Don't share secrets between repositories unnecessarily
- Don't use admin-level tokens when public_repo is enough
- Don't set secrets as environment variables in workflow files

## Troubleshooting

### Issue: "Secret not found" in workflow

**Check:**
1. Secret name matches exactly (case-sensitive)
2. Secret is set at repository level (not organization)
3. Workflow has permission to access secrets

**Fix:**
```yaml
# In workflow file, use exact secret name:
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}  # Correct
  # NOT: ${{ secrets.gemini_api_key }}  # Wrong - case matters
```

### Issue: "Unauthorized" or "Invalid credentials"

**Possible causes:**
1. Secret value is incorrect
2. API key expired
3. API key doesn't have required permissions

**Fix:**
1. Delete the secret in GitHub
2. Generate a new API key
3. Add it again as a secret

### Issue: Tests pass locally but fail in GitHub Actions

**Check:**
1. Local `.env` has different values than secrets
2. Workflow isn't setting environment variables correctly
3. Kaggle credentials need both .env vars AND kaggle.json

**Fix for Kaggle:**
```yaml
# Set both environment variables AND create kaggle.json
- name: Configure Kaggle
  env:
    KAGGLE_USERNAME: ${{ secrets.KAGGLE_USERNAME }}
    KAGGLE_KEY: ${{ secrets.KAGGLE_KEY }}
  run: |
    mkdir -p ~/.kaggle
    echo '{"username":"${{ secrets.KAGGLE_USERNAME }}","key":"${{ secrets.KAGGLE_KEY }}"}' > ~/.kaggle/kaggle.json
    chmod 600 ~/.kaggle/kaggle.json
```

### Issue: GitHub Token rate limits

Without `GH_TOKEN`:
- 60 requests/hour

With `GH_TOKEN`:
- 5,000 requests/hour

**Recommendation:** Always set GH_TOKEN for integration tests.

## Viewing Test Results

### 1. From Actions Tab

1. Go to **Actions** tab
2. Click on the workflow run
3. Click on a job (e.g., "Integration Tests")
4. View logs and test output

### 2. Download Artifacts

1. Scroll to bottom of workflow run
2. Find **Artifacts** section
3. Download:
   - `unit-test-results` - Unit test HTML report
   - `integration-test-results` - Integration test HTML report
   - Coverage reports

### 3. PR Comments

For pull requests, workflows automatically comment results:

```
## Unit Test Results
✅ Unit tests completed. Check artifacts for detailed results.

## Integration Test Results
✅ Integration tests completed. All API connections verified.
```

## Updating Secrets

### To Update a Secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on the secret name
3. Click **Update secret**
4. Enter new value
5. Click **Update secret**

### To Delete a Secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on the secret name
3. Click **Remove secret**
4. Confirm deletion

## Monitoring

### Check Secret Usage

GitHub provides audit logs:

1. Go to **Settings** → **Security** → **Audit log**
2. Filter by "secret"
3. View when secrets were accessed

### Failed Test Notifications

If tests fail, the workflow:
1. Creates a GitHub Issue automatically
2. Labels it with `test-failure` and `automation`
3. Includes link to failed workflow run

## Quick Reference

### Adding New Secret

```bash
# 1. Get the value (example for Gemini)
#    Visit: https://makersuite.google.com/app/apikey

# 2. Add to GitHub
#    Settings → Secrets and variables → Actions
#    → New repository secret
#    Name: GEMINI_API_KEY
#    Secret: <paste value>
#    → Add secret

# 3. Test it
#    Actions → Test On-Demand → Run workflow
#    Select: credentials
```

### Secret Names Reference

```yaml
secrets.GEMINI_API_KEY      # Gemini AI
secrets.KAGGLE_USERNAME     # Kaggle user
secrets.KAGGLE_KEY          # Kaggle API key
secrets.GH_TOKEN            # GitHub token (note: different from GITHUB_TOKEN)
```

## Next Steps

1. ✅ Add all 4 secrets to GitHub
2. ✅ Run credential verification workflow
3. ✅ Push code to trigger automated tests
4. ✅ Verify tests pass in Actions tab
5. ✅ Set up secret rotation reminder (90 days)

---

**Questions?** See [TESTING-GUIDE.md](TESTING-GUIDE.md) for test execution details.
