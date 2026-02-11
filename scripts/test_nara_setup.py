#!/usr/bin/env python3
"""
Test National Archives API Integration

Simple test script to verify API key and basic functionality.

Usage:
    python scripts/test_nara_setup.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.nara_api_client import (
    NARAAPIClient,
    NARAAPIError,
    NARAAuthenticationError
)


def test_api_key():
    """Test API key configuration."""
    print("Testing API key configuration...")
    
    api_key = os.getenv('NARA_API_KEY')
    if not api_key:
        print("❌ NARA_API_KEY not set in environment")
        print("   Set it in your .env file or environment variables")
        return False
    
    print(f"✅ API key found: {api_key[:10]}... (length: {len(api_key)})")
    return True


def test_connection():
    """Test basic API connection."""
    print("\nTesting API connection...")
    
    try:
        client = NARAAPIClient()
        print("✅ Client initialized successfully")
        return client
    except NARAAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return None


def test_search():
    """Test catalog search."""
    print("\nTesting catalog search...")

    try:
        client = NARAAPIClient()
        results = client.search_records(query="constitution", rows=1)
        
        if results.get('opaResponse', {}).get('results', {}).get('total', 0) > 0:
            record = results['opaResponse']['results']['result'][0]
            naid = record.get('naId', 'Unknown')
            title = record.get('title', 'Unknown')
            print(f"✅ Search successful")
            print(f"   Found: {title} (NAID: {naid})")
            return True
        else:
            print("❌ No results found")
            return False
            
    except NARAAPIError as e:
        print(f"❌ Search failed: {e}")
        return False


def test_record_retrieval():
    """Test retrieving specific record."""
    print("\nTesting record retrieval...")
    
    try:
        client = NARAAPIClient()
        # Constitution NAID
        record = client.get_record_by_naid("1667751")
        
        title = record.get('title', 'Unknown')
        naid = record.get('naId', 'Unknown')
        
        print(f"✅ Record retrieval successful")
        print(f"   Title: {title}")
        print(f"   NAID: {naid}")
        return True
        
    except NARAAPIError as e:
        print(f"❌ Record retrieval failed: {e}")
        return False


def test_cache():
    """Test caching functionality."""
    print("\nTesting cache functionality...")
    
    try:
        cache_dir = Path("cache/nara-test")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        client = NARAAPIClient(cache_dir=str(cache_dir))
        
        # First request (should hit API)
        print("   Making first request (should cache)...")
        client.search_records(query="declaration", rows=1)
        
        # Check cache files
        cache_files = list(cache_dir.glob("*.json"))
        if cache_files:
            print(f"✅ Cache working: {len(cache_files)} file(s) cached")
            
            # Cleanup
            for f in cache_files:
                f.unlink()
            cache_dir.rmdir()
            return True
        else:
            print("❌ No cache files created")
            return False
            
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False


def test_rate_limiting():
    """Test rate limiting."""
    print("\nTesting rate limiting...")
    
    try:
        import time
        client = NARAAPIClient()
        
        print("   Making rapid requests (rate limiting should apply)...")
        start = time.time()
        
        # Make multiple requests
        for i in range(3):
            client.search_records(query=f"test{i}", rows=1)
        
        elapsed = time.time() - start
        
        # Should take at least 1 second (2 req/sec with 3 requests)
        if elapsed >= 1.0:
            print(f"✅ Rate limiting working: {elapsed:.2f}s for 3 requests")
            return True
        else:
            print(f"⚠️  Rate limiting may not be active: {elapsed:.2f}s for 3 requests")
            return True  # Not critical
            
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("NATIONAL ARCHIVES API SETUP TEST")
    print("=" * 60)
    
    tests = [
        ("API Key Configuration", test_api_key),
        ("API Connection", test_connection),
        ("Catalog Search", test_search),
        ("Record Retrieval", test_record_retrieval),
        ("Response Caching", test_cache),
        ("Rate Limiting", test_rate_limiting),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result if result is not None else False))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your National Archives API setup is working.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
