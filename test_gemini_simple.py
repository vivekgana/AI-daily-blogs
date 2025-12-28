#!/usr/bin/env python3
"""Simple test script to verify Gemini API fix."""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_api():
    """Test Gemini API with the updated package."""
    print("\n" + "=" * 80)
    print("GEMINI API TEST")
    print("=" * 80)

    # Check if google-generativeai is installed
    try:
        import google.generativeai as genai
        print("[PASS] google-generativeai imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import google-generativeai: {e}")
        print("\nPlease run: pip install -r requirements.txt")
        return False

    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("[SKIP] GEMINI_API_KEY not set in environment")
        print("Set the API key to run full tests")
        return None

    # Configure API
    try:
        genai.configure(api_key=api_key)
        print("[PASS] API configured successfully")
    except Exception as e:
        print(f"[FAIL] Failed to configure API: {e}")
        return False

    # List available models
    try:
        print("\nListing available models...")
        models = genai.list_models()
        found_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
                found_models.append(m.name)

        if found_models:
            print(f"\n[PASS] Found {len(found_models)} compatible models")
        else:
            print("[FAIL] No models found with generateContent support")
            return False

    except Exception as e:
        print(f"[FAIL] Error listing models: {type(e).__name__}: {e}")
        return False

    # Test generator initialization
    try:
        print("\nTesting GeminiGenerator initialization...")
        from src.generators.gemini_generator import GeminiGenerator
        from src.utils.config_loader import ConfigLoader

        config = ConfigLoader()
        generator = GeminiGenerator(config)

        print("[PASS] GeminiGenerator initialized successfully")

        # Test simple generation
        print("\nTesting content generation...")
        test_comps = [{
            'title': 'Test ML Competition',
            'reward': '$10,000',
            'teamCount': 150,
            'complexity_level': 'High'
        }]

        result = generator.generate_competition_overview(test_comps)

        if result and "[Content generation failed" not in result:
            print(f"[PASS] Content generated ({len(result)} chars)")
            print("\nSample output (first 200 chars):")
            print("-" * 80)
            print(result[:200] + "..." if len(result) > 200 else result)
            print("-" * 80)
            return True
        else:
            print(f"[FAIL] Generation returned error:")
            print(result)
            return False

    except Exception as e:
        print(f"[FAIL] Test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    result = test_gemini_api()

    print("\n" + "=" * 80)
    if result is True:
        print("RESULT: All tests PASSED")
        sys.exit(0)
    elif result is None:
        print("RESULT: Tests SKIPPED (no API key)")
        sys.exit(0)
    else:
        print("RESULT: Tests FAILED")
        sys.exit(1)
