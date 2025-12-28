#!/usr/bin/env python3
"""
Test Gemini API and list available models.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

def test_gemini_api():
    """Test Gemini API and list available models."""
    print("=" * 60)
    print("Gemini API Model Test")
    print("=" * 60)
    print()

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not set in .env file")
        return

    # Mask the key for display
    masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]
    print(f"API Key: {masked_key}")
    print()

    try:
        import google.generativeai as genai

        # Configure API
        print("Configuring Gemini API...")
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
        print()

        # List available models
        print("Listing available models...")
        print("-" * 60)

        models = genai.list_models()
        supported_models = []

        for model in models:
            # Check if model supports generateContent
            if 'generateContent' in model.supported_generation_methods:
                supported_models.append(model.name)
                print(f"✅ {model.name}")
                print(f"   Display Name: {model.display_name}")
                print(f"   Description: {model.description[:100]}...")
                print()

        print("-" * 60)
        print(f"\nFound {len(supported_models)} models that support generateContent")
        print()

        # Test with the first available model
        if supported_models:
            test_model = supported_models[0]
            print(f"Testing with model: {test_model}")
            print()

            try:
                model = genai.GenerativeModel(test_model)
                response = model.generate_content("Say 'Hello, AI!' if you can read this.")

                print("✅ Test generation successful!")
                print(f"Response: {response.text}")
                print()

                print("=" * 60)
                print("RECOMMENDED MODEL FOR CONFIG:")
                print("=" * 60)
                # Extract just the model name without the prefix
                model_name = test_model.split('/')[-1]
                print(f"Use this in config.yaml:")
                print(f"  gemini:")
                print(f"    model: '{model_name}'")
                print()

            except Exception as e:
                print(f"❌ Test generation failed: {e}")

    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Install with: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

        # Check if it's an authentication error
        if "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
            print()
            print("The API key appears to be invalid.")
            print("Please check:")
            print("1. Go to: https://makersuite.google.com/app/apikey")
            print("2. Create a new API key")
            print("3. Update GEMINI_API_KEY in your .env file")


if __name__ == '__main__':
    test_gemini_api()
