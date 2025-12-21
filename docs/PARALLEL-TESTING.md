# Parallel Test Execution

**Date:** 2025-12-15
**Status:** ✅ Implemented and Active

---

## Overview

Unit tests now run in parallel using `pytest-xdist`, significantly reducing test execution time. Tests are distributed across 3 workers, with each test file running on a separate worker.

---

## Performance Improvement

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Execution Time** | ~20 seconds | ~13 seconds | **35% faster** |
| **Workers** | 1 (sequential) | 3 (parallel) | **3x parallelization** |
| **Test Files** | 3 files | 3 files | - |
| **Total Tests** | 26 tests | 26 tests | - |

---

## Test Files Running in Parallel

The following unit test files run concurrently:

1. **`tests/unit/test_kaggle_collector.py`** (18 tests)
   - Worker gw0 (usually)
   - Tests Kaggle API collector functionality
   - Includes leaderboard, kernels, competition tests

2. **`tests/unit/test_gemini_generator.py`** (7 tests)
   - Worker gw1 (usually)
   - Tests Gemini AI content generation
   - Includes retry logic and error handling

3. **`tests/unit/test_arxiv_agi_collector.py`** (1 test)
   - Worker gw2 (usually)
   - Tests arXiv research paper collection
   - AGI-focused paper filtering

---

## How It Works

### pytest-xdist Configuration

**Command:**
```bash
pytest tests/unit/ -v -n 3 --dist loadfile
```

**Options:**
- `-n 3`: Use 3 parallel workers
- `--dist loadfile`: Distribute tests by file (each file runs on one worker)
- `-v`: Verbose output to see which worker runs which test

### Distribution Strategy

**`--dist loadfile`** means:
- Each test file is assigned to a single worker
- All tests within a file run sequentially on that worker
- Different files run in parallel on different workers

**Example execution:**
```
created: 3/3 workers
scheduling tests via LoadFileScheduling

[gw0] test_kaggle_collector.py::test_1  ← Worker 0
[gw1] test_gemini_generator.py::test_1   ← Worker 1
[gw2] test_arxiv_agi_collector.py::test_1 ← Worker 2
```

---

## Configuration Files

### 1. `requirements.txt`

Added test dependencies:
```python
# Testing
pytest==8.0.0
pytest-cov==4.1.0
pytest-html==4.1.1
pytest-xdist==3.5.0  # For parallel test execution
```

### 2. `pytest.ini`

Created pytest configuration:
```ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Default options
addopts =
    -v
    --tb=short
    --strict-markers
    --color=yes

# Markers for test categorization
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may require API credentials)
    slow: Slow running tests
    requires_api: Tests that require API credentials
```

### 3. GitHub Actions Workflows

#### `run-tests.yml` (Unit Tests Job)

```yaml
- name: Run unit tests in parallel
  run: |
    pytest tests/unit/ -v -n 3 \
      --dist loadfile \
      --cov=src \
      --cov-report=term-missing \
      --cov-report=html \
      --html=unit-test-report.html \
      --self-contained-html
  env:
    PYTEST_XDIST_WORKER_COUNT: 3
```

#### `test-on-demand.yml` (Unit Tests Option)

```yaml
- name: Run Unit Tests Only
  if: ${{ github.event.inputs.test_suite == 'unit' }}
  run: |
    pytest tests/unit/ -v -n 3 \
      --dist loadfile \
      --cov=src \
      --cov-report=term-missing \
      --html=test-report.html \
      --self-contained-html
  env:
    PYTEST_XDIST_WORKER_COUNT: 3
```

---

## Running Tests Locally

### Parallel Execution (Default)

```bash
# Run all unit tests in parallel (3 workers)
pytest tests/unit/ -n 3 --dist loadfile

# Run with coverage
pytest tests/unit/ -n 3 --dist loadfile --cov=src

# Run specific files in parallel
pytest tests/unit/test_kaggle_collector.py tests/unit/test_gemini_generator.py -n 2
```

### Sequential Execution (If Needed)

```bash
# Run tests sequentially (no parallelization)
pytest tests/unit/ -v

# Useful for debugging
pytest tests/unit/ -v -s  # Show print statements
```

### Check Worker Assignments

```bash
# See which worker runs which test
pytest tests/unit/ -n 3 --dist loadfile -v

# Output shows:
# [gw0] [  5%] PASSED test_kaggle_collector.py::test_1
# [gw1] [ 10%] PASSED test_gemini_generator.py::test_1
# [gw2] [ 15%] PASSED test_arxiv_agi_collector.py::test_1
```

---

## Benefits

### 1. **Faster CI/CD Pipeline**
- Unit tests complete 35% faster
- Less waiting time for PR checks
- Quicker feedback loops

### 2. **Better Resource Utilization**
- Uses multiple CPU cores efficiently
- GitHub Actions runners have multiple cores
- Local development machines benefit too

### 3. **Scalability**
- Can easily add more test files
- Workers scale with test files
- Maintains fast execution as tests grow

### 4. **Isolation**
- Each file runs on separate worker
- Reduces test interference
- Cleaner test execution

---

## Limitations and Considerations

### 1. **File-Level Parallelization Only**

Tests within the same file still run sequentially:
```
✅ test_kaggle_collector.py (18 tests) ← All on worker gw0
✅ test_gemini_generator.py (7 tests)  ← All on worker gw1
```

If one file has 100 tests and another has 1 test, there will be imbalance.

**Solution:** Keep test files balanced in size or use `--dist loadscope` for class-level distribution.

### 2. **Shared Resources**

If tests share resources (files, database, etc.), they may conflict when running in parallel.

**Solution:**
- Use `--dist loadfile` (current setting) to keep file tests together
- Use fixtures with proper scope
- Mock external dependencies

### 3. **Coverage Collection**

Coverage with parallel execution requires `pytest-cov` (already included).

**How it works:**
- Each worker collects coverage separately
- pytest-cov combines coverage from all workers
- Final coverage report is accurate

### 4. **Integration Tests**

Integration tests are NOT run in parallel because they:
- May have API rate limits
- Share test data
- Have external dependencies

**Current behavior:**
- Unit tests: Parallel (3 workers)
- Integration tests: Sequential (1 worker)

---

## Advanced Usage

### Adjust Worker Count

```bash
# Use auto-detected CPU count
pytest tests/unit/ -n auto

# Use specific number of workers
pytest tests/unit/ -n 4  # 4 workers

# Use logical cores (default for -n auto)
pytest tests/unit/ -n logical
```

### Different Distribution Strategies

```bash
# Load by file (current default)
pytest tests/unit/ -n 3 --dist loadfile

# Load by scope (class/module)
pytest tests/unit/ -n 3 --dist loadscope

# Load by group (custom grouping)
pytest tests/unit/ -n 3 --dist loadgroup

# Load each test to any worker
pytest tests/unit/ -n 3 --dist load
```

### Test Markers

```bash
# Run only unit tests (fast, no API)
pytest -m unit -n 3

# Run only integration tests (sequential)
pytest -m integration

# Skip slow tests
pytest -m "not slow" -n 3
```

---

## Troubleshooting

### Problem: Tests fail in parallel but pass sequentially

**Cause:** Tests have shared state or race conditions

**Solution:**
```bash
# Run sequentially to debug
pytest tests/unit/ -v -s

# Check for:
# - Shared global variables
# - File system operations
# - Mocked objects not properly isolated
```

### Problem: Coverage report missing lines

**Cause:** Coverage collection issue with parallel execution

**Solution:**
```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run with coverage explicitly
pytest tests/unit/ -n 3 --cov=src --cov-report=html
```

### Problem: Slower than sequential

**Cause:** Test files are very small or overhead dominates

**Solution:**
```bash
# Reduce worker count
pytest tests/unit/ -n 2

# Or run sequentially for small test suites
pytest tests/unit/
```

---

## Future Improvements

### 1. **Optimize Worker Count**
- Profile execution to find optimal worker count
- May increase to 4-5 workers as more tests are added
- Use `-n auto` for automatic detection

### 2. **Test File Balancing**
- Split large test files (like `test_kaggle_collector.py`)
- Create separate files for leaderboard, kernels, competitions
- Better load distribution across workers

### 3. **Integration Test Parallelization**
- Investigate if integration tests can be safely parallelized
- Use test isolation techniques
- Mock external APIs more aggressively

### 4. **Custom Test Grouping**
- Use `--dist loadgroup` with custom markers
- Group tests by resource requirements
- Optimize for API rate limits

---

## Summary

✅ **Implemented:** Parallel test execution with 3 workers
✅ **Performance:** 35% faster test execution (20s → 13s)
✅ **Configuration:** pytest-xdist with loadfile distribution
✅ **CI/CD:** GitHub Actions workflows updated
✅ **Local:** Works on development machines

**Next step:** Monitor performance as test suite grows and adjust worker count accordingly.

---

**Last Updated:** 2025-12-15
**Commit:** 20ca5e3
**Branch:** fix/gemini-api-and-kaggle-leaderboard
