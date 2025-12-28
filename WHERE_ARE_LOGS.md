# Where Are GitHub Actions Logs? 📋

Quick guide to finding logs when GitHub Actions runs.

---

## 🎯 Quick Answer

**Logs are in 2 places:**

1. **Live Console Logs** → GitHub Actions web interface
2. **Downloaded Logs** → Artifacts (ZIP files)

---

## 📍 Method 1: View Live Logs (Recommended)

### Step 1: Go to Actions Tab
👉 https://github.com/vivekgana/AI-daily-blogs/actions

### Step 2: Click on a Workflow Run
Example: "Run Tests #42"

### Step 3: Click on a Job
Example: "Unit Tests" or "Integration Tests"

### Step 4: Click on a Step
Example: "Run unit tests"

### What You See:
```
Run pytest tests/unit/ -v
============================= test session starts =============================
collected 25 items

tests/unit/test_gemini_generator.py ........ PASSED
tests/unit/test_kaggle_collector.py ........ PASSED

========================== 25 passed in 3.45s ==========================
```

### 💡 Pro Tip: Use Search
- Click 🔍 icon in top right
- Search for: "ERROR", "FAILED", "404", etc.

---

## 📦 Method 2: Download Log Artifacts

### When Workflow Completes:

**Step 1: Go to Workflow Run**
https://github.com/vivekgana/AI-daily-blogs/actions

**Step 2: Scroll to Bottom**
Look for "Artifacts" section

**Step 3: Download ZIP File**
Click on artifact name:
- `error-logs` - Application logs
- `unit-test-results` - Test reports
- `integration-test-results` - Integration reports

**Step 4: Extract & View**
- Unzip the file
- Open HTML reports in browser
- View log files in text editor

---

## 📂 What's Inside Artifacts

### error-logs.zip
```
logs/
  ├── app.log              # Main application log
  ├── error.log            # Error messages
  ├── kaggle_collector.log # Kaggle API logs
  └── blog_generator.log   # Blog generation logs
```

### unit-test-results.zip
```
├── unit-test-report.html  # Open this in browser!
└── htmlcov/
    └── index.html         # Coverage report
```

---

## 🔍 Finding Specific Logs

### For Test Failures:

1. **Go to Actions** → Failed workflow run
2. **Click failed job** (red X icon)
3. **Search for "FAILED"**
4. **Look above for error message**

**Example:**
```
FAILED tests/integration/test_kaggle.py::test_get_competitions

E   AssertionError: assert 0 > 0
E    +  where 0 = len([])

tests/integration/test_kaggle.py:45: AssertionError
```

This tells you:
- **File:** test_kaggle.py
- **Test:** test_get_competitions
- **Line:** 45
- **Problem:** Empty list returned

### For API Errors:

**Search for:**
- `401` - Authentication failed
- `404` - Not found
- `500` - Server error
- `ERROR` - All errors

---

## 📊 Log Locations

### During GitHub Actions:

```
Runner Workspace:
  /home/runner/work/AI-daily-blogs/AI-daily-blogs/

  logs/                    ← Your application logs
    ├── app.log
    ├── error.log
    └── ...

  *.html                   ← Test reports
  htmlcov/                 ← Coverage reports
```

### After Workflow (Artifacts):

```
GitHub Artifacts (downloadable):

  error-logs.zip           ← Application logs (7 days)
  unit-test-results.zip    ← Test reports (30 days)
  integration-test-results.zip
```

### Locally (Your Computer):

```
c:\Users\gekambaram\source\personal\AI-daily-blogs\

  logs\                    ← Created when you run locally
    ├── app.log
    ├── error.log
    └── ...

  *.html                   ← Test reports
  htmlcov\                 ← Coverage reports
```

---

## 🎯 Common Scenarios

### Scenario 1: Test Failed - What Went Wrong?

```
1. Actions tab → Failed run → Failed job
2. Search: "FAILED"
3. Read error message
4. Fix code
5. Push changes (workflow runs again)
```

### Scenario 2: Blog Generation Failed

```
1. Check email notification (has workflow link)
2. Click link → Open workflow run
3. Click "Generate blog" job
4. Search: "ERROR"
5. Download error-logs.zip for details
6. Fix issue and re-run
```

### Scenario 3: Want to See Test Coverage

```
1. Actions tab → Any completed run
2. Scroll to bottom → Artifacts
3. Download "unit-test-results"
4. Extract → Open htmlcov/index.html
5. See coverage per file
```

---

## 📧 Email Notifications

When workflows fail, you get an email with:

```
Subject: [vivekgana/AI-daily-blogs] Run failed: Generate Daily Blog

The run failed on branch: main

View workflow run:
https://github.com/vivekgana/AI-daily-blogs/actions/runs/12345
```

**Click the link** to see logs immediately!

---

## 💡 Quick Tips

### See More Details:
Add to your workflow (in workflow file):
```yaml
env:
  ACTIONS_RUNNER_DEBUG: true
```

### Add Custom Logs:
In your Python code:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Starting process...")
logger.error(f"Failed: {error}")
```

### Keep Logs Longer:
In workflow file:
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: my-logs
    path: logs/
    retention-days: 90  # Instead of 7
```

---

## 🔗 Quick Links

**Your Logs:**
- All runs: https://github.com/vivekgana/AI-daily-blogs/actions
- Latest run: https://github.com/vivekgana/AI-daily-blogs/actions/workflows/generate-daily-blog.yml

**Need More Help?**
- Full guide: [docs/GITHUB-ACTIONS-LOGS.md](docs/GITHUB-ACTIONS-LOGS.md)
- GitHub docs: https://docs.github.com/actions/monitoring-and-troubleshooting-workflows

---

## 📝 Summary

| What | Where | How |
|------|-------|-----|
| **Live logs** | Actions tab → Run → Job → Step | Click to view |
| **Application logs** | Artifacts → error-logs.zip | Download ZIP |
| **Test reports** | Artifacts → test-results.zip | Download & open HTML |
| **Coverage** | Artifacts → unit-test-results → htmlcov/ | Open index.html |
| **Search** | In log view → Click 🔍 | Type "ERROR", etc. |

---

**Most Common:** Just go to Actions tab and click on the workflow run! 🚀
