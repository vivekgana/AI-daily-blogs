# 🔐 Credentials Setup Guide

Quick guide to set up API credentials for local testing.

## 📋 Quick Start (5 Minutes)

### 1. Copy the template

```bash
# The .env file already exists, just edit it
code .env  # or use your favorite editor
```

### 2. Get your API keys

| Service | Get Key From | Required |
|---------|-------------|----------|
| **Gemini** | https://makersuite.google.com/app/apikey | ✅ Yes |
| **Kaggle** | https://www.kaggle.com/settings/account → API | ✅ Yes |
| **GitHub** | https://github.com/settings/tokens | ⚠️ Optional |

### 3. Fill in your `.env` file

```bash
# Gemini API
GEMINI_API_KEY=AIzaSyC...your_actual_key

# Kaggle API
KAGGLE_USERNAME=your_username
KAGGLE_KEY=1234567890abcdef...your_key

# GitHub API (optional - for better rate limits)
GITHUB_TOKEN=ghp_...your_token
```

### 4. Test your setup

```bash
python test_local_credentials.py
```

Expected output:
```
[PASS] Gemini API
[PASS] Kaggle API
[PASS] GitHub API
*** All credentials configured correctly!
```

## 🎯 Get Your API Keys

### Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)

### Kaggle API Credentials

**Method 1: Download kaggle.json**
1. Visit: https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New Token"
4. Download `kaggle.json`
5. Open it and copy username and key to `.env`

**Method 2: Place kaggle.json file**
```bash
# Windows
mkdir %USERPROFILE%\.kaggle
move kaggle.json %USERPROFILE%\.kaggle\

# Linux/Mac
mkdir ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### GitHub Token (Optional)

1. Visit: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: "AI Daily Blogs Local Testing"
4. Scopes: Check **`public_repo`** only
5. Click "Generate token"
6. Copy the token (starts with `ghp_...`)

**Note:** Without token, GitHub API works but with rate limits (60 requests/hour vs 5000 with token)

## ✅ Verify Setup

### Quick Test
```bash
python test_local_credentials.py
```

### Run Integration Tests
```bash
# Test all collectors
pytest tests/integration/test_collectors_integration.py -v

# Test specific collector
pytest tests/integration/test_collectors_integration.py::TestKaggleCollectorIntegration -v
```

### Run Full Blog Generation
```bash
python src/main.py
```

## ❌ Troubleshooting

### "GEMINI_API_KEY not found"

**Check 1:** Verify .env file exists
```bash
ls -la .env  # Should show the file
```

**Check 2:** Verify no typos in key name
```bash
cat .env | grep GEMINI  # Should show: GEMINI_API_KEY=...
```

**Check 3:** Install python-dotenv
```bash
pip install python-dotenv
```

### "Could not find kaggle.json"

**Option 1:** Use .env instead (recommended)
```bash
# Add to .env:
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

**Option 2:** Place kaggle.json in correct location
```bash
# Windows: %USERPROFILE%\.kaggle\kaggle.json
# Linux/Mac: ~/.kaggle/kaggle.json
```

### "GitHub rate limit exceeded"

**Solution:** Add GITHUB_TOKEN to .env
- Without token: 60 requests/hour
- With token: 5,000 requests/hour

### "404 NotFound: models/gemini-1.5-flash"

**Solution:** Update package
```bash
pip install --upgrade google-generativeai>=0.8.0
```

## 🔒 Security Notes

### ✅ DO
- Keep `.env` file local only
- Use different keys for dev/prod
- Rotate keys regularly
- Use app passwords for Gmail

### ❌ DON'T
- Never commit `.env` to git
- Never share keys in chat/email
- Never hardcode credentials
- Never use main Gmail password

## 📚 Next Steps

1. ✅ Set up credentials (you are here)
2. Run credential test: `python test_local_credentials.py`
3. Run unit tests: `pytest tests/unit/ -v`
4. Run integration tests: `pytest tests/integration/ -v`
5. Generate blog: `python src/main.py`

## 📖 Full Documentation

See [docs/LOCAL-SETUP-GUIDE.md](docs/LOCAL-SETUP-GUIDE.md) for complete details.

---

**Questions?** Check the troubleshooting section above or the full setup guide.
