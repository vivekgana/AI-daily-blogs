# Run Tests Now - Quick Guide

**Status:** Token updated ✅
**Next:** Trigger test workflow

## Option 1: Via GitHub Web Interface (2 minutes)

### Step-by-Step:

1. **Go to Actions tab:**
   https://github.com/vivekgana/AI-daily-blogs/actions

2. **Select workflow:**
   - Click "Test On-Demand" in the left sidebar

3. **Run credential test:**
   - Click "Run workflow" button (top right)
   - Branch: `fix/gemini-api-and-kaggle-leaderboard`
   - Test suite: Select `credentials`
   - Verbose: Leave unchecked
   - Click green "Run workflow" button

4. **Wait for results (30 seconds):**
   - Workflow will appear at the top of the list
   - Status will change from 🟡 to ✅ or ❌
   - Click on the workflow run to see details

### Expected Output:

```
======================================================================
CREDENTIAL VERIFICATION (GitHub Secrets)
======================================================================
✅ GEMINI_API_KEY: Set (length: XX)
✅ KAGGLE_USERNAME: Set (length: XX)
✅ KAGGLE_KEY: Set (length: XX)
✅ GITHUB_TOKEN: Set (length: XX)
======================================================================
Result: 4/4 credentials configured

✅ All credentials configured correctly!
```

## Option 2: Via GitHub CLI (Faster)

If your terminal has GitHub CLI available:

```bash
# Make sure you're in the project directory
cd c:\Users\gekambaram\source\personal\AI-daily-blogs

# Trigger credential test
gh workflow run test-on-demand.yml \
  -f test_suite=credentials \
  -f verbose=false \
  --ref fix/gemini-api-and-kaggle-leaderboard

# Watch the workflow run
gh run watch
```

Or view in browser:
```bash
gh workflow view test-on-demand.yml --web
```

## After Credential Test Passes

Run the full test suite:

### Via Web Interface:
1. Go to Actions → Test On-Demand
2. Click "Run workflow"
3. Branch: `fix/gemini-api-and-kaggle-leaderboard`
4. Test suite: Select `all`
5. Click "Run workflow"

### Via GitHub CLI:
```bash
gh workflow run test-on-demand.yml \
  -f test_suite=all \
  -f verbose=false \
  --ref fix/gemini-api-and-kaggle-leaderboard

gh run watch
```

### Expected Results:
```
Unit Tests: ✅ 25/25 passed
Integration Tests: ✅ 15+/15+ passed
Total: ✅ 40+ tests passed
```

## Test Suite Options

You can test specific components:

| Test Suite | What It Tests | Time |
|-----------|---------------|------|
| `credentials` | All secrets configured | 30 sec |
| `all` | Unit + Integration tests | 3-5 min |
| `unit` | Unit tests only | 1 min |
| `integration` | Integration tests only | 2-3 min |
| `kaggle` | Kaggle API only | 1 min |
| `github` | GitHub API only | 30 sec |
| `research` | arXiv API only | 30 sec |

## Troubleshooting

### Issue: "401 Unauthorized" (Kaggle)

**Problem:** `KAGGLE_PASSWORD` secret contains account password instead of API key

**Fix:**
1. Go to: https://www.kaggle.com/settings/account
2. Click "Create New Token"
3. Download `kaggle.json`
4. Open file, copy the `key` value (40 characters)
5. Go to: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
6. Click on `KAGGLE_PASSWORD`
7. Click "Update secret"
8. Paste the API key value
9. Click "Update secret"
10. Re-run the workflow

### Issue: "Bad credentials" (GitHub)

**Problem:** `MY_GITHUB_ACTION` token invalid/expired

**Fix:**
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select `public_repo` scope only
4. Copy the token (starts with `ghp_`)
5. Go to: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
6. Click on `MY_GITHUB_ACTION`
7. Click "Update secret"
8. Paste the token
9. Click "Update secret"
10. Re-run the workflow

### Issue: "API key not valid" (Gemini)

**Problem:** `GEMINI_API_KEY` invalid

**Fix:**
1. Go to: https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy the key (starts with `AIzaSy`)
4. Go to: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
5. Click on `GEMINI_API_KEY`
6. Click "Update secret"
7. Paste the key
8. Click "Update secret"
9. Re-run the workflow

## Quick Links

- **Actions:** https://github.com/vivekgana/AI-daily-blogs/actions
- **Secrets:** https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
- **Workflows:** https://github.com/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml

## After Tests Pass

1. **Create PR** (if not already created):
   ```bash
   gh pr create --title "Fix: Gemini API 404 error and Kaggle leaderboard rank bug + comprehensive testing" --body-file .github/PR_DESCRIPTION.md --base main --head fix/gemini-api-and-kaggle-leaderboard
   ```

2. **Or use web link:**
   https://github.com/vivekgana/AI-daily-blogs/compare/main...fix/gemini-api-and-kaggle-leaderboard?expand=1

3. **Merge PR** after all checks pass

---

## Quick Start (Right Now)

**Fastest way to test:**

1. Click: https://github.com/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml
2. Click: "Run workflow"
3. Select: `credentials`
4. Click: "Run workflow"
5. Wait 30 seconds
6. Check results

**That's it!** 🚀
