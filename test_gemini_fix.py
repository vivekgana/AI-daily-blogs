#!/usr/bin/env python3
"""Test script to verify Gemini API fix."""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_model_listing():
    """Test listing available Gemini models."""
    print("=" * 80)
    print("TEST 1: Listing Available Gemini Models")
    print("=" * 80)

    try:
        import google.generativeai as genai

        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not set in environment")
            return False

        # Configure API
        genai.configure(api_key=api_key)

        # List models
        print("\n✅ Available Gemini models that support generateContent:")
        models = genai.list_models()
        found_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
                found_models.append(m.name)

        if not found_models:
            print("❌ No models found with generateContent support")
            return False

        print(f"\n✅ Found {len(found_models)} compatible models")
        return True

    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        print("\n💡 Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error listing models: {type(e).__name__}: {e}")
        return False


def test_gemini_initialization():
    """Test Gemini generator initialization."""
    print("\n" + "=" * 80)
    print("TEST 2: Gemini Generator Initialization")
    print("=" * 80)

    try:
        from src.generators.gemini_generator import GeminiGenerator
        from src.utils.config_loader import ConfigLoader

        # Load config
        config = ConfigLoader()

        # Initialize generator
        print("\n⏳ Initializing Gemini generator...")
        generator = GeminiGenerator(config)

        print(f"✅ Generator initialized successfully")
        print(f"   Model: {generator.model._model_name if hasattr(generator.model, '_model_name') else 'Unknown'}")

        return True

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Initialization failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_generation():
    """Test simple content generation."""
    print("\n" + "=" * 80)
    print("TEST 3: Simple Content Generation")
    print("=" * 80)

    try:
        from src.generators.gemini_generator import GeminiGenerator
        from src.utils.config_loader import ConfigLoader

        # Initialize
        config = ConfigLoader()
        generator = GeminiGenerator(config)

        # Test simple generation
        print("\n⏳ Testing content generation...")

        test_competitions = [
            {
                'title': 'Test ML Competition',
                'reward': '$10,000',
                'teamCount': 150,
                'complexity_level': 'High',
                'url': 'https://kaggle.com/test'
            }
        ]

        result = generator.generate_competition_overview(test_competitions)

        if result and "[Content generation failed" not in result:
            print(f"✅ Content generated successfully ({len(result)} characters)")
            print("\n📄 Sample output (first 200 chars):")
            print("-" * 80)
            print(result[:200] + "..." if len(result) > 200 else result)
            print("-" * 80)
            return True
        else:
            print(f"❌ Generation returned error or empty content:")
            print(result)
            return False

    except Exception as e:
        print(f"❌ Generation test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\nGEMINI API FIX VERIFICATION TESTS")
    print("=" * 80)

    results = []

    # Test 1: List models
    results.append(("Model Listing", test_gemini_model_listing()))

    # Test 2: Initialize generator
    results.append(("Generator Init", test_gemini_initialization()))

    # Test 3: Generate content
    results.append(("Content Generation", test_simple_generation()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n*** All tests passed! Gemini API is working correctly.")
        return 0
    else:
        print(f"\n*** {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
