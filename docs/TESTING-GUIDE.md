# Testing Guide - AI Daily Blogs

**Document Version:** 1.0
**Last Updated:** 2025-11-30
**Author:** gekambaram

## Table of Contents

1. [Test Overview](#test-overview)
2. [Setup Prerequisites](#setup-prerequisites)
3. [Running Tests](#running-tests)
4. [Test Types](#test-types)
5. [CI/CD Integration](#cicd-integration)

## Test Overview

The project includes comprehensive test coverage:

| Test Type | Count | Purpose |
|-----------|-------|---------|
| Unit Tests | 25+ | Test individual components |
| Integration Tests | 15+ | Test API connections and workflows |
| Credential Tests | 5 | Verify API credentials |

## Setup Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Edit `.env` file with your actual API keys:

```bash
# Gemini API
GEMINI_API_KEY=AIzaSy...your_real_key

# Kaggle API
KAGGLE_USERNAME=your_actual_username
KAGGLE_KEY=your_actual_40char_key

# GitHub API (optional)
GITHUB_TOKEN=ghp_...your_real_token
```

See [CREDENTIALS-SETUP.md](../CREDENTIALS-SETUP.md) for detailed instructions.

### 3. Verify Setup

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

## Running Tests

### Quick Test Commands

```bash
# Test credentials
python test_local_credentials.py

# Run all unit tests
pytest tests/unit/ -v

# Run all integration tests
pytest tests/integration/ -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Specific Test Suites

```bash
# Gemini generator tests
pytest tests/unit/test_gemini_generator.py -v

# Kaggle collector tests
pytest tests/unit/test_kaggle_collector.py -v

# Integration tests for all collectors
pytest tests/integration/test_collectors_integration.py -v

# Specific collector integration
pytest tests/integration/test_collectors_integration.py::TestKaggleCollectorIntegration -v
```

## Test Types

### 1. Unit Tests

**Location:** `tests/unit/`

Test individual components in isolation with mocked dependencies.

#### Gemini Generator Tests (7 tests)

```bash
pytest tests/unit/test_gemini_generator.py -v
```

Tests:
- ✅ Initialization success
- ✅ No API key handling
- ✅ Competition overview generation
- ✅ Retry logic (success on 2nd attempt)
- ✅ All retries fail handling
- ✅ Empty response handling
- ✅ Authentication error handling

#### Kaggle Collector Tests (18 tests)

```bash
pytest tests/unit/test_kaggle_collector.py -v
```

Tests:
- ✅ Initialization and authentication
- ✅ Active competitions fetching
- ✅ Competition ranking algorithm
- ✅ Prize value extraction
- ✅ Leaderboard retrieval (7 tests)
  - Success case
  - Empty/None handling
  - Missing attributes
  - Error handling
- ✅ Kernel fetching (3 tests)
- ✅ Complexity assessment (2 tests)
- ✅ Industry relevance

### 2. Integration Tests

**Location:** `tests/integration/`

Test real API connections with actual credentials.

#### Collectors Integration Tests (15+ tests)

```bash
pytest tests/integration/test_collectors_integration.py -v
```

**Kaggle Collector Integration (5 tests)**
- Get active competitions
- Rank competitions
- Get leaderboard data
- Get kernels
- Extract prize values

**GitHub Collector Integration (2 tests)**
- Search repositories
- Discover competition repos

**Research Collector Integration (3 tests)**
- Fetch recent papers
- Search by keyword
- Filter by category

**End-to-End Tests (3 tests)**
- Kaggle → GitHub workflow
- Research relevance
- Data completeness

### 3. Credential Tests

**Location:** `test_local_credentials.py`

Quick validation of API credentials.

```bash
python test_local_credentials.py
```

Tests:
1. .env file exists and loads
2. Gemini API key works
3. Kaggle credentials work
4. GitHub token works (optional)
5. Email credentials exist (optional)

## Test Results Format

### Successful Test Run

```
============================= test session starts =============================
tests/unit/test_gemini_generator.py::TestGeminiGenerator::test_initialization_success PASSED
tests/unit/test_gemini_generator.py::TestGeminiGenerator::test_generate_competition_overview PASSED
...
======================== 25 passed, 0 failed in 5.23s =========================
```

### Failed Test

```
FAILED tests/unit/test_gemini_generator.py::TestGeminiGenerator::test_authentication_error_handling
AssertionError: Expected 'Authentication error' in result
```

### Skipped Test

```
tests/integration/test_collectors_integration.py::TestKaggleCollectorIntegration::test_01 SKIPPED
Reason: Kaggle credentials not configured
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to main/feature branches
- Pull request creation
- Daily schedule (7 AM EST)

**Workflow:** `.github/workflows/generate-daily-blog.yml`

```yaml
- name: Run Tests
  run: |
    pytest tests/unit/ -v
    pytest tests/integration/ -v --html=test-report.html
```

### Required Secrets

Set in GitHub repository settings → Secrets:

| Secret | Purpose | Required |
|--------|---------|----------|
| `GEMINI_API_KEY` | AI content generation | ✅ Yes |
| `KAGGLE_USERNAME` | Competition data | ✅ Yes |
| `KAGGLE_KEY` | Competition data | ✅ Yes |
| `GITHUB_TOKEN` | Repo search | ⚠️ Optional |
| `EMAIL_USERNAME` | Notifications | ⚠️ Optional |
| `EMAIL_PASSWORD` | Notifications | ⚠️ Optional |

## Test Coverage

### Current Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

Expected coverage:
- `src/generators/gemini_generator.py`: 90%+
- `src/collectors/kaggle_collector.py`: 85%+
- `src/collectors/github_collector.py`: 75%+
- `src/collectors/research_collector.py`: 70%+

### View Coverage HTML Report

```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

## Troubleshooting Tests

### Issue: "Kaggle credentials not found"

**Solution 1:** Set credentials in .env
```bash
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

**Solution 2:** Place kaggle.json
```bash
# Windows
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\

# Linux/Mac
mkdir ~/.kaggle
cp kaggle.json ~/.kaggle/
```

### Issue: "Gemini API 404 error"

**Solution:** Update package
```bash
pip install --upgrade google-generativeai>=0.8.0
```

### Issue: "Rate limit exceeded (GitHub)"

**Solution:** Add GITHUB_TOKEN to .env
- Without token: 60 requests/hour
- With token: 5,000 requests/hour

### Issue: "Integration tests failing"

**Check:**
1. Are credentials valid?
2. Is internet connection working?
3. Are APIs down? (check status pages)
4. Are rate limits exceeded?

**Debug:**
```bash
# Run with verbose output
pytest tests/integration/ -v -s

# Run single test
pytest tests/integration/test_collectors_integration.py::TestKaggleCollectorIntegration::test_01_get_active_competitions -v -s
```

### Issue: "Import errors"

**Solution:** Reinstall dependencies
```bash
pip uninstall -y google-generativeai kaggle PyGithub
pip install -r requirements.txt
```

## Best Practices

### Writing New Tests

1. **Unit Tests**
   - Mock external dependencies
   - Test one thing at a time
   - Use descriptive test names
   - Add docstrings

2. **Integration Tests**
   - Check for credentials first
   - Handle API failures gracefully
   - Use skipTest() when appropriate
   - Test realistic scenarios

3. **Test Data**
   - Don't hardcode competition IDs
   - Handle varying API responses
   - Test edge cases
   - Validate data structures

### Test Naming Convention

```python
# Unit tests
def test_<component>_<scenario>()
def test_get_leaderboard_success()
def test_generate_content_retry_logic()

# Integration tests
def test_<number>_<action>()
def test_01_get_active_competitions()
def test_02_rank_competitions()
```

### Running Tests Locally Before Commit

```bash
# 1. Run unit tests (fast)
pytest tests/unit/ -v

# 2. Run integration tests (requires credentials)
pytest tests/integration/ -v

# 3. Check coverage
pytest tests/ --cov=src --cov-report=term-missing

# 4. Run specific failing test
pytest tests/unit/test_gemini_generator.py::TestGeminiGenerator::test_authentication_error_handling -v
```

## Continuous Improvement

### Adding New Tests

1. Identify untested code paths
2. Write failing test first (TDD)
3. Implement fix
4. Verify test passes
5. Update this documentation

### Monitoring Test Health

- All unit tests should pass 100%
- Integration tests may skip without credentials
- Coverage should be >80% for critical code
- Tests should run in <30 seconds (unit)
- Tests should run in <5 minutes (integration)

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python test_local_credentials.py` | Verify credentials |
| `pytest tests/unit/ -v` | Run unit tests |
| `pytest tests/integration/ -v` | Run integration tests |
| `pytest tests/ --cov=src` | Run with coverage |
| `pytest -k "leaderboard"` | Run tests matching keyword |
| `pytest -x` | Stop on first failure |
| `pytest --lf` | Run last failed |

---

**Questions?** See [CREDENTIALS-SETUP.md](../CREDENTIALS-SETUP.md) or [LOCAL-SETUP-GUIDE.md](LOCAL-SETUP-GUIDE.md)
