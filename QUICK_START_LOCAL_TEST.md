# Quick Start: Test Locally with GitHub Secrets

**Goal:** Test blog generation locally using the same credentials as GitHub Actions

---

## 🚀 Quick 5-Step Process

### Step 1: Authenticate GitHub CLI (One-time setup)
```powershell
gh auth login --web
```
Follow the browser prompts to authenticate.

### Step 2: Verify GitHub Secrets Are Configured
```powershell
.\verify_github_secrets.ps1
```
This checks that secrets exist in GitHub (you should see all required secrets listed).

### Step 3: Set Environment Variables
```powershell
.\set_github_secrets_env.ps1
```
This will ask you for your actual credentials and set environment variables.

**Get credentials from:**
- Kaggle: https://www.kaggle.com/settings/account → "Create New Token"
- Gemini: https://makersuite.google.com/app/apikey → "Create API key"

### Step 4: Test API Connectivity
```bash
python test_with_github_secrets.py
```
This verifies all APIs work with your credentials.

### Step 5: Run Blog Generation
```bash
python test_blog_generation_local.py
```
Generates a full blog post locally.

---

## ✅ Expected Results

**Step 2 output:**
```
[FOUND] KAGGLE_USERNAME
[FOUND] KAGGLE_PASSWORD
[FOUND] GEMINI_API_KEY
[SUCCESS] All required secrets are configured!
```

**Step 4 output:**
```
[PASS] Kaggle API
[PASS] Gemini API
[SUCCESS] All required API connections working!
```

**Step 5 output:**
```
[PASS] Environment
[PASS] Credentials
[PASS] API Connections
[PASS] Data Collectors
[PASS] Blog Generation
[PASS] Output Validation

Result: 6/6 steps passed
```

---

## 🔧 Troubleshooting

**Problem:** GitHub CLI not authenticated
```powershell
# Clear conflicting token
$env:GITHUB_TOKEN = $null

# Re-authenticate
gh auth login --web
```

**Problem:** 401 Unauthorized from Kaggle
- Download fresh `kaggle.json` from Kaggle website
- Use the exact `username` and `key` values
- Make sure environment variables are set correctly

**Problem:** Gemini API error
- Create new API key at https://makersuite.google.com/app/apikey
- Set `$env:GEMINI_API_KEY` with new key

---

## 📚 Detailed Documentation

For comprehensive guides, see:
- [TEST_GITHUB_SECRETS_CONNECTIVITY.md](TEST_GITHUB_SECRETS_CONNECTIVITY.md) - Complete testing guide
- [RUN_LOCAL_TEST_WITH_GITHUB_SECRETS.md](RUN_LOCAL_TEST_WITH_GITHUB_SECRETS.md) - Environment setup guide

---

## 🎯 Why This Approach?

✅ **Same as CI/CD:** Uses identical credentials as GitHub Actions
✅ **Secure:** Credentials in environment variables, not files
✅ **Verifiable:** Can check secrets exist before testing
✅ **Consistent:** If it works locally, it works in GitHub Actions

---

**Start here:** Run Step 1 to authenticate GitHub CLI! 🚀
