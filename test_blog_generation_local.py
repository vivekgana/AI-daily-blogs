#!/usr/bin/env python3
"""Local blog generation test script.

This script tests the full blog generation pipeline locally:
1. Tests all API connections
2. Generates today's blog
3. Validates output files
4. Shows preview of generated content
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_step_1_environment():
    """Test 1: Check environment setup."""
    print_header("TEST 1: Environment Setup")

    # Check .env file
    if os.path.exists('.env'):
        print("[PASS] .env file found")
    else:
        print("[FAIL] .env file not found")
        print("       Run: cp .env.example .env")
        print("       Then add your API keys")
        return False

    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[PASS] Environment variables loaded")
    except ImportError:
        print("[FAIL] python-dotenv not installed")
        print("       Run: pip install python-dotenv")
        return False

    return True

def test_step_2_credentials():
    """Test 2: Verify API credentials."""
    print_header("TEST 2: API Credentials")

    from dotenv import load_dotenv
    load_dotenv()

    credentials = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'KAGGLE_USERNAME': os.getenv('KAGGLE_USERNAME'),
        'KAGGLE_KEY': os.getenv('KAGGLE_KEY'),
    }

    all_valid = True
    for name, value in credentials.items():
        if value and len(value) > 10 and not value.startswith('your_'):
            print(f"[PASS] {name}: Set (length: {len(value)})")
        else:
            print(f"[FAIL] {name}: Not configured or invalid")
            all_valid = False

    if not all_valid:
        print("\n[INFO] Update your .env file with real API keys")
        print("       See CREDENTIALS-SETUP.md for help")
        return False

    return True

def test_step_3_api_connections():
    """Test 3: Test API connections."""
    print_header("TEST 3: API Connections")

    from dotenv import load_dotenv
    load_dotenv()

    # Test Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content("Say 'Hello!'")
        if hasattr(response, 'text') and response.text:
            print(f"[PASS] Gemini API: Connected")
        else:
            print(f"[FAIL] Gemini API: No response")
            return False
    except Exception as e:
        print(f"[FAIL] Gemini API: {type(e).__name__}: {e}")
        return False

    # Test Kaggle
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        competitions = api.competitions_list()
        print(f"[PASS] Kaggle API: Connected ({len(competitions)} competitions)")
    except Exception as e:
        print(f"[FAIL] Kaggle API: {type(e).__name__}: {e}")
        return False

    # Test GitHub (optional)
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token and len(github_token) > 10:
        try:
            from github import Github
            gh = Github(github_token)
            user = gh.get_user()
            print(f"[PASS] GitHub API: Connected (user: {user.login})")
        except Exception as e:
            print(f"[WARN] GitHub API: {type(e).__name__}: {e}")
    else:
        print(f"[SKIP] GitHub API: No token configured (optional)")

    return True

def test_step_4_collectors():
    """Test 4: Test data collectors."""
    print_header("TEST 4: Data Collectors")

    from src.collectors.kaggle_collector import KaggleCollector
    from src.collectors.github_collector import GitHubCollector
    from src.collectors.research_collector import ResearchCollector
    from src.utils.config_loader import ConfigLoader

    config = ConfigLoader()

    # Test Kaggle Collector
    try:
        kaggle = KaggleCollector(config)
        competitions = kaggle.get_active_competitions()
        print(f"[PASS] Kaggle Collector: Retrieved {len(competitions)} competitions")

        if competitions:
            ranked = kaggle.rank_competitions(competitions)
            print(f"[PASS] Kaggle Ranking: Ranked {len(ranked)} competitions")
        else:
            print(f"[WARN] Kaggle Ranking: No competitions to rank")
    except Exception as e:
        print(f"[FAIL] Kaggle Collector: {type(e).__name__}: {e}")
        return False

    # Test GitHub Collector
    try:
        github = GitHubCollector(config)
        repos = github.search_repositories("xgboost", max_results=5)
        print(f"[PASS] GitHub Collector: Retrieved {len(repos)} repositories")
    except Exception as e:
        print(f"[WARN] GitHub Collector: {type(e).__name__}: {e}")

    # Test Research Collector
    try:
        research = ResearchCollector(config)
        papers = research.fetch_recent_papers("machine learning", max_results=5)
        print(f"[PASS] Research Collector: Retrieved {len(papers)} papers")
    except Exception as e:
        print(f"[WARN] Research Collector: {type(e).__name__}: {e}")

    return True

def test_step_5_blog_generation():
    """Test 5: Generate blog."""
    print_header("TEST 5: Blog Generation")

    try:
        from src.generators.blog_generator import BlogGenerator
        from src.utils.config_loader import ConfigLoader

        config = ConfigLoader()
        generator = BlogGenerator(config)

        print("[INFO] Generating blog... (this may take 30-60 seconds)")
        today = datetime.now().strftime('%Y-%m-%d')

        result = generator.generate_daily_blog()

        if result and 'success' in result:
            print(f"[PASS] Blog generation: Success")
            print(f"       Date: {today}")

            if 'markdown_path' in result:
                print(f"       Markdown: {result['markdown_path']}")
            if 'html_path' in result:
                print(f"       HTML: {result['html_path']}")

            return result
        else:
            print(f"[FAIL] Blog generation: Failed")
            if result and 'error' in result:
                print(f"       Error: {result['error']}")
            return None

    except Exception as e:
        print(f"[FAIL] Blog generation: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_step_6_validate_output(result):
    """Test 6: Validate generated files."""
    print_header("TEST 6: Output Validation")

    if not result:
        print("[FAIL] No blog generated to validate")
        return False

    # Check markdown file
    if 'markdown_path' in result:
        md_path = result['markdown_path']
        if os.path.exists(md_path):
            size = os.path.getsize(md_path)
            print(f"[PASS] Markdown file: {md_path}")
            print(f"       Size: {size:,} bytes")
        else:
            print(f"[FAIL] Markdown file not found: {md_path}")
            return False

    # Check HTML file
    if 'html_path' in result:
        html_path = result['html_path']
        if os.path.exists(html_path):
            size = os.path.getsize(html_path)
            print(f"[PASS] HTML file: {html_path}")
            print(f"       Size: {size:,} bytes")
        else:
            print(f"[FAIL] HTML file not found: {html_path}")
            return False

    return True

def show_preview(result):
    """Show preview of generated content."""
    print_header("BLOG PREVIEW")

    if not result or 'markdown_path' not in result:
        print("[INFO] No preview available")
        return

    md_path = result['markdown_path']
    if not os.path.exists(md_path):
        print("[INFO] Markdown file not found")
        return

    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Show first 50 lines
        lines = content.split('\n')[:50]
        preview = '\n'.join(lines)

        print(preview)

        if len(content.split('\n')) > 50:
            print("\n... (truncated, see full file for complete content) ...")

        print(f"\n[INFO] Full content: {md_path}")
        print(f"[INFO] Total lines: {len(content.split('\n'))}")
        print(f"[INFO] Total characters: {len(content):,}")

    except Exception as e:
        print(f"[ERROR] Could not read preview: {e}")

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" LOCAL BLOG GENERATION TEST")
    print("=" * 70)
    print(f" Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = []

    # Test 1: Environment
    if not test_step_1_environment():
        print("\n[ABORT] Cannot proceed without environment setup")
        return 1
    results.append(("Environment", True))

    # Test 2: Credentials
    if not test_step_2_credentials():
        print("\n[ABORT] Cannot proceed without valid credentials")
        return 1
    results.append(("Credentials", True))

    # Test 3: API Connections
    if not test_step_3_api_connections():
        print("\n[ABORT] Cannot proceed with failed API connections")
        return 1
    results.append(("API Connections", True))

    # Test 4: Collectors
    if not test_step_4_collectors():
        print("\n[ABORT] Cannot proceed with failed collectors")
        return 1
    results.append(("Data Collectors", True))

    # Test 5: Blog Generation
    blog_result = test_step_5_blog_generation()
    if blog_result:
        results.append(("Blog Generation", True))

        # Test 6: Validation
        if test_step_6_validate_output(blog_result):
            results.append(("Output Validation", True))

            # Show preview
            show_preview(blog_result)
        else:
            results.append(("Output Validation", False))
    else:
        results.append(("Blog Generation", False))

    # Summary
    print_header("SUMMARY")

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\nResult: {passed_count}/{total} steps passed")

    if passed_count == total:
        print("\n*** All tests passed!")
        print("    Blog generated successfully!")
        print("\n    Next steps:")
        print("    1. Review the generated blog files")
        print("    2. Check formatting and content quality")
        print("    3. Commit to git if satisfied")
        print("    4. Push to trigger GitHub Actions")
        return 0
    else:
        print("\n*** Some tests failed")
        print("    Review errors above and fix issues")
        return 1

if __name__ == '__main__':
    sys.exit(main())
