#!/usr/bin/env python3
"""
Comprehensive test runner for AI Daily Blogs.

Runs all tests: unit, integration, and scenario tests.
"""
import sys
import unittest
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up test environment
os.environ.setdefault('PYTHONPATH', str(Path(__file__).parent))


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def run_unit_tests():
    """Run all unit tests."""
    print_header("UNIT TESTS")

    loader = unittest.TestLoader()
    suite = loader.discover('tests/unit', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful(), result


def run_scenario_tests():
    """Run all scenario tests."""
    print_header("SCENARIO TESTS (Error Handling & Edge Cases)")

    loader = unittest.TestLoader()
    suite = loader.discover('tests/scenario', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful(), result


def run_integration_tests():
    """Run integration tests (requires API keys)."""
    print_header("INTEGRATION TESTS (Requires API Keys & Internet)")

    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  GEMINI_API_KEY not set - Skipping integration tests")
        print("   Set GEMINI_API_KEY environment variable to run integration tests")
        return True, None

    print(f"✅ GEMINI_API_KEY found")

    loader = unittest.TestLoader()
    suite = loader.discover('tests/integration', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful(), result


def print_summary(results):
    """Print test summary."""
    print_header("TEST SUMMARY")

    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0

    for name, (success, result) in results.items():
        if result:
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            total_skipped += len(result.skipped)

            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} - {name}")
            print(f"   Tests: {result.testsRun}, "
                  f"Failures: {len(result.failures)}, "
                  f"Errors: {len(result.errors)}, "
                  f"Skipped: {len(result.skipped)}")
        else:
            print(f"⚠️  SKIPPED - {name}")

    print("\n" + "-"*80)
    print(f"TOTAL: {total_tests} tests, "
          f"{total_failures} failures, "
          f"{total_errors} errors, "
          f"{total_skipped} skipped")

    all_passed = all(success for success, _ in results.values() if _ is not None)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print("\n❌ SOME TESTS FAILED")

    print("="*80 + "\n")

    return all_passed


def main():
    """Main test runner."""
    start_time = datetime.now()

    print("\n" + "="*80)
    print("  AI DAILY BLOGS - COMPREHENSIVE TEST SUITE")
    print(f"  Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    results = {}

    # Run unit tests
    try:
        success, result = run_unit_tests()
        results['Unit Tests'] = (success, result)
    except Exception as e:
        print(f"❌ Unit tests crashed: {e}")
        results['Unit Tests'] = (False, None)

    # Run scenario tests
    try:
        success, result = run_scenario_tests()
        results['Scenario Tests'] = (success, result)
    except Exception as e:
        print(f"❌ Scenario tests crashed: {e}")
        results['Scenario Tests'] = (False, None)

    # Run integration tests
    try:
        success, result = run_integration_tests()
        results['Integration Tests'] = (success, result)
    except Exception as e:
        print(f"❌ Integration tests crashed: {e}")
        results['Integration Tests'] = (False, None)

    # Print summary
    all_passed = print_summary(results)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"Test execution completed in {duration:.2f} seconds")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
