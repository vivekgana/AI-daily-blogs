# Local Development Setup Guide

**Document Version:** 1.0
**Last Updated:** 2025-11-30
**Author:** gekambaram

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [API Credentials Setup](#api-credentials-setup)
3. [Environment Configuration](#environment-configuration)
4. [Testing Locally](#testing-locally)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.11 or higher
- Git
- Text editor (VS Code recommended)

## API Credentials Setup

### 1. Gemini API Key

**Get your API key:**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

**Important:** Keep this key secure and never commit it to git!

### 2. Kaggle API Credentials

**Option A: Download kaggle.json (Recommended)**

1. Visit [Kaggle Account Settings](https://www.kaggle.com/settings/account)
2. Scroll to "API" section
3. Click "Create New Token"
4. This downloads `kaggle.json` file

**Option B: Get credentials from kaggle.json**

If you already have `kaggle.json`, extract the credentials:

```json
{
  "username": "your_username",
  "key": "your_40_character_api_key"
}
```

### 3. Email Credentials (Optional)

If you want email notifications:

1. Use a Gmail account
2. Enable 2-Factor Authentication
3. Generate an [App Password](https://myaccount.google.com/apppasswords)
4. Use this app password (not your regular Gmail password)

## Environment Configuration

### Method 1: Using .env File (Recommended)

**Step 1: Create .env file**

Copy the example file:

```bash
cp .env.example .env
```

**Step 2: Edit .env file**

Open `.env` in your text editor and fill in your credentials:

```bash
# Gemini API
GEMINI_API_KEY=AIzaSy...your_actual_key_here

# Kaggle API
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_40_character_kaggle_api_key

# Email (Optional)
EMAIL_USERNAME=your.email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_TO=recipient@example.com
```

**Step 3: Verify .env is ignored by git**

```bash
# Should output: .env
git check-ignore .env

# Should NOT show .env in the list
git status
```

### Method 2: Using Kaggle JSON File (For Kaggle Only)

**Step 1: Create .kaggle directory**

```bash
# Windows
mkdir %USERPROFILE%\.kaggle

# Linux/Mac
mkdir ~/.kaggle
```

**Step 2: Place kaggle.json**

```bash
# Windows
move kaggle.json %USERPROFILE%\.kaggle\kaggle.json

# Linux/Mac
mv kaggle.json ~/.kaggle/kaggle.json
```

**Step 3: Set permissions (Linux/Mac only)**

```bash
chmod 600 ~/.kaggle/kaggle.json
```

**Step 4: Still need Gemini in .env**

Create `.env` file with at least:

```bash
GEMINI_API_KEY=AIzaSy...your_actual_key_here
```

### Method 3: Using Environment Variables (Windows)

**Step 1: Set system environment variables**

```powershell
# PowerShell (Run as Administrator)
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('KAGGLE_USERNAME', 'your_username', 'User')
[System.Environment]::SetEnvironmentVariable('KAGGLE_KEY', 'your_key_here', 'User')
```

Or use Windows GUI:
1. Search "Environment Variables" in Windows
2. Click "Environment Variables" button
3. Under "User variables", click "New"
4. Add each variable name and value

**Step 2: Restart your terminal/IDE**

Environment variables require a restart to take effect.

### Method 3: Using Environment Variables (Linux/Mac)

**Step 1: Edit shell profile**

```bash
# For bash
nano ~/.bashrc

# For zsh
nano ~/.zshrc
```

**Step 2: Add exports**

```bash
# Gemini API
export GEMINI_API_KEY="your_key_here"

# Kaggle API
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_key_here"

# Email (Optional)
export EMAIL_USERNAME="your.email@gmail.com"
export EMAIL_PASSWORD="your_app_password"
export EMAIL_TO="recipient@example.com"
```

**Step 3: Reload profile**

```bash
# For bash
source ~/.bashrc

# For zsh
source ~/.zshrc
```

## Testing Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Quick Test - Gemini API

Create a test file `test_local_gemini.py`:

```python
#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Test Gemini
try:
    import google.generativeai as genai

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        exit(1)

    print(f"✅ GEMINI_API_KEY found (length: {len(api_key)})")

    # Configure and test
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    response = model.generate_content("Say hello!")
    print(f"✅ Gemini API working! Response: {response.text[:50]}...")

except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    exit(1)

print("\n✅ All tests passed!")
```

Run it:

```bash
python test_local_gemini.py
```

### 3. Quick Test - Kaggle API

Create a test file `test_local_kaggle.py`:

```python
#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Test Kaggle
try:
    from kaggle.api.kaggle_api_extended import KaggleApi

    # Check for credentials
    username = os.getenv('KAGGLE_USERNAME')
    key = os.getenv('KAGGLE_KEY')

    if username and key:
        print(f"✅ Kaggle credentials from .env")
        print(f"   Username: {username}")
        print(f"   Key: {key[:10]}..." if len(key) > 10 else f"   Key: {key}")

        # Set credentials
        os.environ['KAGGLE_USERNAME'] = username
        os.environ['KAGGLE_KEY'] = key
    else:
        print("⚠️  Kaggle credentials from ~/.kaggle/kaggle.json")

    # Test API
    api = KaggleApi()
    api.authenticate()
    print("✅ Kaggle API authenticated!")

    # List competitions
    comps = api.competitions_list()
    print(f"✅ Found {len(comps)} competitions")
    print(f"   First competition: {comps[0].title if comps else 'None'}")

except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    exit(1)

print("\n✅ All tests passed!")
```

Run it:

```bash
python test_local_kaggle.py
```

### 4. Run Unit Tests

```bash
# Run all tests
pytest tests/unit/ -v

# Run specific tests
pytest tests/unit/test_gemini_generator.py -v
pytest tests/unit/test_kaggle_collector.py -v
```

### 5. Run Full Blog Generation

```bash
python src/main.py
```

Check output in `blogs/` directory.

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"

**Solution 1: Check .env file exists**

```bash
# Windows
dir .env

# Linux/Mac
ls -la .env
```

**Solution 2: Verify .env content**

```bash
# Windows
type .env

# Linux/Mac
cat .env
```

**Solution 3: Check python-dotenv is installed**

```bash
pip install python-dotenv
pip show python-dotenv
```

**Solution 4: Add manual load in code**

If using Python directly:

```python
from dotenv import load_dotenv
load_dotenv()  # Add this at the top of your script
```

### Issue: "Could not find kaggle.json"

**Solution 1: Create .kaggle directory**

```bash
# Windows
mkdir %USERPROFILE%\.kaggle

# Linux/Mac
mkdir ~/.kaggle
```

**Solution 2: Use .env instead**

Add to `.env`:
```
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

**Solution 3: Verify file location**

```bash
# Windows
dir %USERPROFILE%\.kaggle\kaggle.json

# Linux/Mac
ls -l ~/.kaggle/kaggle.json
```

### Issue: "404 NotFound: models/gemini-1.5-flash"

**Solution:** You're using old package version

```bash
pip install --upgrade google-generativeai>=0.8.0
```

### Issue: Kaggle leaderboard returns empty

**Possible causes:**

1. **Competition has private leaderboard** - This is normal
2. **Wrong competition ID** - Check the competition URL
3. **API rate limit** - Wait a few minutes
4. **Authentication issue** - Re-check credentials

**Debug:**

```python
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

# Test specific competition
comp_id = 'titanic'  # Use actual competition ID
leaderboard = api.competition_leaderboard_view(comp_id)
print(f"Leaderboard entries: {len(leaderboard) if leaderboard else 0}")
```

### Issue: Import errors

**Solution:** Reinstall dependencies

```bash
pip uninstall -y google-generativeai kaggle
pip install -r requirements.txt
```

## Security Best Practices

### DO ✅

- Use `.env` file for local development
- Add `.env` to `.gitignore` (already done)
- Use different credentials for dev/prod
- Rotate API keys regularly
- Use app passwords for Gmail (not main password)

### DON'T ❌

- Never commit `.env` file to git
- Never commit `kaggle.json` to git
- Never hardcode credentials in code
- Never share credentials in chat/email
- Never commit credentials in config files

## Quick Reference

### Check if credentials are loaded:

```python
import os
from dotenv import load_dotenv

load_dotenv()

print(f"GEMINI_API_KEY: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Not set'}")
print(f"KAGGLE_USERNAME: {'✅ Set' if os.getenv('KAGGLE_USERNAME') else '❌ Not set'}")
print(f"KAGGLE_KEY: {'✅ Set' if os.getenv('KAGGLE_KEY') else '❌ Not set'}")
```

### Environment variable priority (highest to lowest):

1. System environment variables
2. `.env` file in project root
3. `~/.kaggle/kaggle.json` (Kaggle only)

### File locations:

| File | Windows | Linux/Mac |
|------|---------|-----------|
| `.env` | `.\\.env` | `./.env` |
| `kaggle.json` | `%USERPROFILE%\\.kaggle\\kaggle.json` | `~/.kaggle/kaggle.json` |

## Next Steps

1. ✅ Set up credentials using one of the methods above
2. ✅ Run the quick tests to verify setup
3. ✅ Run unit tests: `pytest tests/unit/ -v`
4. ✅ Try blog generation: `python src/main.py`
5. ✅ Check output in `blogs/` directory

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Verify credentials are correct
3. Check API rate limits
4. Review error logs in `logs/` directory
5. Run tests with `-v` flag for verbose output

---

**Document End**
