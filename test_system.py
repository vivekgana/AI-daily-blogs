#!/usr/bin/env python3
"""Test script to validate the Kaggle blog automation system."""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all module imports."""
    print("=" * 60)
    print("Testing Module Imports")
    print("=" * 60)

    tests = [
        ("Config Loader", "from src.utils.config_loader import ConfigLoader"),
        ("Logger", "from src.utils.logger import setup_logger"),
        ("Error Handler", "from src.utils.error_handler import ErrorHandler"),
        ("Kaggle Collector", "from src.collectors.kaggle_collector import KaggleCollector"),
        ("GitHub Collector", "from src.collectors.github_collector import GitHubCollector"),
        ("Research Collector", "from src.collectors.research_collector import ResearchCollector"),
        ("Gemini Generator", "from src.generators.gemini_generator import GeminiGenerator"),
        ("Blog Generator", "from src.generators.blog_generator import BlogGenerator"),
    ]

    passed = 0
    failed = 0

    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✓ {name:<25} PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {name:<25} FAILED: {e}")
            failed += 1

    print(f"\nImport Tests: {passed} passed, {failed} failed")
    return failed == 0


def test_config_loading():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("Testing Configuration Loading")
    print("=" * 60)

    try:
        from src.utils.config_loader import ConfigLoader

        config = ConfigLoader()

        # Test key access
        top_n = config.get('competition_selection.top_n')
        print(f"✓ Top N competitions: {top_n}")

        weights = config.get('competition_selection.ranking_weights')
        print(f"✓ Ranking weights: {weights}")

        blog_dir = config.get('blog.output_dir')
        print(f"✓ Blog output directory: {blog_dir}")

        gemini_model = config.get('gemini.model')
        print(f"✓ Gemini model: {gemini_model}")

        print("\n✓ Configuration loading: PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Configuration loading: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logger():
    """Test logger setup."""
    print("\n" + "=" * 60)
    print("Testing Logger")
    print("=" * 60)

    try:
        from src.utils.logger import setup_logger

        logger = setup_logger("test_logger", log_dir="logs")
        logger.info("Test log message")
        logger.debug("Debug message")
        logger.warning("Warning message")

        print("✓ Logger setup and logging: PASSED")
        return True

    except Exception as e:
        print(f"✗ Logger: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_templates():
    """Test template files exist and are valid."""
    print("\n" + "=" * 60)
    print("Testing Templates")
    print("=" * 60)

    try:
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        # Test Markdown template
        md_template = env.get_template('blog_template.md')
        print(f"✓ Markdown template loaded: {md_template.name}")

        # Test HTML template
        html_template = env.get_template('blog_template.html')
        print(f"✓ HTML template loaded: {html_template.name}")

        print("\n✓ Template loading: PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Template loading: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directory_structure():
    """Test required directories exist."""
    print("\n" + "=" * 60)
    print("Testing Directory Structure")
    print("=" * 60)

    required_dirs = [
        "src",
        "src/collectors",
        "src/generators",
        "src/utils",
        "templates",
        "config",
        ".github/workflows"
    ]

    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path:<30} EXISTS")
        else:
            print(f"✗ {dir_path:<30} MISSING")
            all_exist = False

    print(f"\n{'✓' if all_exist else '✗'} Directory structure: {'PASSED' if all_exist else 'FAILED'}")
    return all_exist


def test_required_files():
    """Test required files exist."""
    print("\n" + "=" * 60)
    print("Testing Required Files")
    print("=" * 60)

    required_files = [
        "requirements.txt",
        "README.md",
        "CLAUDE.md",
        "config/config.yaml",
        ".gitignore",
        "src/main.py",
        "src/collectors/kaggle_collector.py",
        "src/collectors/github_collector.py",
        "src/collectors/research_collector.py",
        "src/generators/gemini_generator.py",
        "src/generators/blog_generator.py",
        "src/utils/config_loader.py",
        "src/utils/logger.py",
        "src/utils/error_handler.py",
        "templates/blog_template.md",
        "templates/blog_template.html",
        ".github/workflows/generate-daily-blog.yml",
        ".github/workflows/deploy-github-pages.yml",
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path:<50} EXISTS")
        else:
            print(f"✗ {file_path:<50} MISSING")
            all_exist = False

    print(f"\n{'✓' if all_exist else '✗'} Required files: {'PASSED' if all_exist else 'FAILED'}")
    return all_exist


def test_yaml_syntax():
    """Test YAML files are valid."""
    print("\n" + "=" * 60)
    print("Testing YAML Syntax")
    print("=" * 60)

    try:
        import yaml

        # Test config.yaml
        with open('config/config.yaml', 'r') as f:
            config_data = yaml.safe_load(f)
        print(f"✓ config/config.yaml is valid YAML")

        # Test workflow files
        workflows = [
            '.github/workflows/generate-daily-blog.yml',
            '.github/workflows/deploy-github-pages.yml',
            '.github/workflows/blank.yml'
        ]

        for workflow in workflows:
            if Path(workflow).exists():
                with open(workflow, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                print(f"✓ {workflow} is valid YAML")

        print("\n✓ YAML syntax: PASSED")
        return True

    except Exception as e:
        print(f"\n✗ YAML syntax: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_requirements():
    """Test requirements.txt is valid."""
    print("\n" + "=" * 60)
    print("Testing Requirements File")
    print("=" * 60)

    try:
        with open('requirements.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        print(f"✓ Found {len(lines)} package requirements")

        # Check for essential packages
        essential = ['kaggle', 'google-generativeai', 'pandas', 'jinja2', 'PyGithub', 'arxiv']
        missing = []

        for pkg in essential:
            if any(pkg in line for line in lines):
                print(f"✓ {pkg:<30} found")
            else:
                print(f"✗ {pkg:<30} MISSING")
                missing.append(pkg)

        if missing:
            print(f"\n✗ Requirements: FAILED - Missing {missing}")
            return False

        print("\n✓ Requirements file: PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Requirements: FAILED - {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("KAGGLE BLOG AUTOMATION - TEST SUITE")
    print("=" * 60)

    results = {
        "Directory Structure": test_directory_structure(),
        "Required Files": test_required_files(),
        "Module Imports": test_imports(),
        "Configuration Loading": test_config_loading(),
        "Logger": test_logger(),
        "Templates": test_templates(),
        "YAML Syntax": test_yaml_syntax(),
        "Requirements": test_requirements(),
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:<30} {status}")

    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
