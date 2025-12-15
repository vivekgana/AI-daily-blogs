# Trigger GitHub Actions Tests Locally (SSL Fix)

**Issue:** SSL certificate verification errors when using curl
**Solution:** Use Python or PowerShell scripts that bypass SSL verification for local testing

## Method 1: Python Script (Recommended)

### Step 1: Set GitHub Token

**Windows Command Prompt:**
```cmd
set MY_GITHUB_ACTION=your_github_token_here
```

**Windows PowerShell:**
```powershell
$env:MY_GITHUB_ACTION="your_github_token_here"
```

### Step 2: Run Script

**Test credentials (quick - 30 seconds):**
```bash
python trigger_github_workflow.py --test-suite credentials
```

**Run all tests (full - 3-5 minutes):**
```bash
python trigger_github_workflow.py --test-suite all
```

**Other test options:**
```bash
python trigger_github_workflow.py --test-suite unit          # Unit tests only
python trigger_github_workflow.py --test-suite integration  # Integration tests
python trigger_github_workflow.py --test-suite kaggle       # Kaggle API only
python trigger_github_workflow.py --test-suite github       # GitHub API only
python trigger_github_workflow.py --test-suite research     # arXiv API only
```

**With verbose output:**
```bash
python trigger_github_workflow.py --test-suite all --verbose
```

## Method 2: PowerShell Script

### Option A: Using Environment Variable

```powershell
# Set token
$env:MY_GITHUB_ACTION="your_github_token_here"

# Run test
.\trigger_test.ps1 -TestSuite credentials
```

### Option B: Passing Token as Parameter

```powershell
.\trigger_test.ps1 -Token "your_github_token_here" -TestSuite credentials
```

### Test Suite Options

```powershell
.\trigger_test.ps1 -TestSuite credentials   # Quick credential check
.\trigger_test.ps1 -TestSuite all          # All tests
.\trigger_test.ps1 -TestSuite unit         # Unit tests only
.\trigger_test.ps1 -TestSuite integration  # Integration tests
.\trigger_test.ps1 -TestSuite kaggle       # Kaggle API only
```

## Method 3: Direct Web Interface (No SSL Issues)

**Fastest and most reliable:**

1. **Click this link:**
   https://github.com/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml

2. **Click "Run workflow" button**

3. **Select:**
   - Branch: `fix/gemini-api-and-kaggle-leaderboard`
   - Test suite: `credentials` (or `all`)

4. **Click "Run workflow"**

5. **View results** (30 seconds - 5 minutes)

## Getting Your GitHub Token

If you don't have a token or need a new one:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: "AI-Daily-Blogs Workflow Trigger"
4. Expiration: 90 days
5. **Scopes:** Check these boxes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
6. Click "Generate token"
7. **Copy the token immediately** (you won't see it again!)

**Token format:** Starts with `ghp_` and is 40+ characters

## Expected Results

### Credential Test (30 seconds)
```
✅ GEMINI_API_KEY: Set (length: XX)
✅ KAGGLE_USERNAME: Set (length: XX)
✅ KAGGLE_KEY: Set (length: XX)
✅ GITHUB_TOKEN: Set (length: XX)

✅ All credentials configured correctly!
```

### All Tests (3-5 minutes)
```
Unit Tests: ✅ 25/25 passed
Integration Tests: ✅ 15+/15+ passed
Coverage: 85%+

Total: ✅ 40+ tests passed
```

## Viewing Results

After triggering the workflow:

**View all workflow runs:**
https://github.com/vivekgana/AI-daily-blogs/actions

**The latest run will be at the top:**
- 🟡 Yellow dot = Running
- ✅ Green checkmark = Passed
- ❌ Red X = Failed

**Click on the run to see:**
- Detailed logs
- Test output
- Error messages (if any)
- Execution time

## Troubleshooting

### Error: "Authentication failed (401)"

**Problem:** Token is invalid, expired, or lacks proper scopes

**Fix:**
1. Generate new token with `repo` and `workflow` scopes
2. Update the token in your command
3. Try again

### Error: "Workflow not found (404)"

**Problem:** Branch not pushed or workflow file missing

**Fix:**
```bash
git status  # Check branch
git push origin fix/gemini-api-and-kaggle-leaderboard  # Push if needed
```

### Error: "SSL Certificate verification failed"

**Problem:** Corporate proxy or SSL inspection

**Fix:** The Python and PowerShell scripts already bypass SSL verification. If still failing:
- Use Method 3 (web interface) instead
- Or check with your IT department about SSL/proxy settings

### Script Not Found

**Python script:**
```bash
# Make sure you're in the right directory
cd c:\Users\gekambaram\source\personal\AI-daily-blogs

# Run script
python trigger_github_workflow.py --test-suite credentials
```

**PowerShell script:**
```powershell
# Make sure you're in the right directory
cd c:\Users\gekambaram\source\personal\AI-daily-blogs

# Allow script execution (first time only)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run script
.\trigger_test.ps1 -TestSuite credentials
```

## Quick Start (Choose One)

### Fastest: Web Interface
1. Click: https://github.com/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml
2. Click "Run workflow"
3. Select `credentials`
4. Click "Run workflow"

### Python Script
```bash
set MY_GITHUB_ACTION=your_token_here
python trigger_github_workflow.py --test-suite credentials
```

### PowerShell Script
```powershell
$env:MY_GITHUB_ACTION="your_token_here"
.\trigger_test.ps1 -TestSuite credentials
```

---

**All three methods trigger the same GitHub Actions workflow.**
**Choose whichever is easiest for you!**

**Most reliable:** Use the web interface (Method 3) - no SSL or authentication issues.
