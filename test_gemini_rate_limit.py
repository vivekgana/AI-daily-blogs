#!/usr/bin/env python3
"""
Test Gemini API with rate limiting.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import time

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config_loader import ConfigLoader
from src.generators.gemini_generator import GeminiGenerator

def test_rate_limiting():
    """Test Gemini API with rate limiting."""
    print("=" * 60)
    print("Gemini API Rate Limit Test")
    print("=" * 60)
    print()

    try:
        # Load configuration
        config = ConfigLoader()
        print("✅ Configuration loaded")

        # Initialize Gemini generator
        generator = GeminiGenerator(config)
        print("✅ Gemini generator initialized")
        print()

        # Test multiple API calls to verify rate limiting
        print("Testing rate limiting with 3 API calls...")
        print("(Should take ~30 seconds with 15s delays)")
        print("-" * 60)

        start_time = time.time()

        # Call 1
        print("\n📝 Call 1: Generating short content...")
        result1 = generator._generate_with_retry("Say 'Test 1 successful' in one sentence.")
        print(f"✅ Response: {result1[:100]}...")

        # Call 2
        print("\n📝 Call 2: Generating short content...")
        result2 = generator._generate_with_retry("Say 'Test 2 successful' in one sentence.")
        print(f"✅ Response: {result2[:100]}...")

        # Call 3
        print("\n📝 Call 3: Generating short content...")
        result3 = generator._generate_with_retry("Say 'Test 3 successful' in one sentence.")
        print(f"✅ Response: {result3[:100]}...")

        elapsed_time = time.time() - start_time

        print()
        print("-" * 60)
        print(f"\n✅ All API calls successful!")
        print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
        print(f"📊 Expected time: ~30 seconds (2 × 15s delays)")
        print()

        if elapsed_time >= 25:
            print("✅ Rate limiting working correctly (proper delays enforced)")
        else:
            print("⚠️  Rate limiting may not be working (too fast)")

        return True

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = test_rate_limiting()
    sys.exit(0 if success else 1)
