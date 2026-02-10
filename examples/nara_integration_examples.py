#!/usr/bin/env python3
"""
Example: National Archives API Integration

Demonstrates various ways to use the National Archives API integration.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.nara_api_client import NARAAPIClient


def example_basic_search():
    """Example: Basic catalog search."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Basic Catalog Search")
    print("=" * 60)
    
    client = NARAAPIClient()
    
    # Search for constitution-related records
    results = client.search_records(
        query="constitution",
        rows=5,
        sort="naId asc"
    )
    
    total = results.get('opaResponse', {}).get('results', {}).get('total', 0)
    print(f"\nFound {total} total results")
    print("\nTop 5 results:")
    
    for record in results['opaResponse']['results']['result']:
        print(f"  • {record.get('title')} (NAID: {record.get('naId')})")


def example_get_specific_document():
    """Example: Get specific document."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Get Specific Document")
    print("=" * 60)
    
    client = NARAAPIClient()
    
    # Get Constitution by NAID
    naid = "1667751"
    record = client.get_record_by_naid(naid)
    
    print(f"\nDocument: {record.get('title')}")
    print(f"NAID: {record.get('naId')}")
    print(f"Type: {record.get('type')}")
    
    # Get description
    description = record.get('scopeContent', {}).get('scopeContentNote', {}).get('note')
    if description:
        print(f"\nDescription: {description[:200]}...")


def example_get_transcription():
    """Example: Get document transcription."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Get Document Transcription")
    print("=" * 60)
    
    client = NARAAPIClient()
    
    naid = "1667751"  # Constitution
    
    # Try to get transcriptions
    try:
        transcriptions = client.get_transcriptions_by_naid(naid)
        
        if transcriptions:
            print(f"\nFound {len(transcriptions)} transcription(s)")
            first = transcriptions[0]
            text = first.get('transcription', '')
            print(f"Preview: {text[:200]}...")
        else:
            print(f"\nNo transcriptions available for NAID {naid}")
    except Exception as e:
        print(f"\nCould not retrieve transcriptions: {e}")


def example_get_extracted_text():
    """Example: Get extracted text."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Get Extracted Text")
    print("=" * 60)
    
    client = NARAAPIClient()
    
    naid = "1667751"  # Constitution
    
    text = client.get_extracted_text(naid)
    
    if text:
        print(f"\nExtracted text length: {len(text)} characters")
        print(f"Preview: {text[:200]}...")
    else:
        print(f"\nNo extracted text available for NAID {naid}")


def example_search_with_filters():
    """Example: Advanced search with filters."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Advanced Search with Filters")
    print("=" * 60)
    
    client = NARAAPIClient()
    
    # Search for treaties from 1780-1800
    results = client.search_records(
        query="treaty",
        rows=10,
        beginYear=1780,
        endYear=1800,
        sort="year asc"
    )
    
    total = results.get('opaResponse', {}).get('results', {}).get('total', 0)
    print(f"\nFound {total} treaties from 1780-1800")
    
    if total > 0:
        print("\nResults:")
        for record in results['opaResponse']['results']['result'][:5]:
            print(f"  • {record.get('title')} (NAID: {record.get('naId')})")


def example_get_child_records():
    """Example: Get child records."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Get Child Records")
    print("=" * 60)
    
    client = NARAAPIClient()
    
    # Get children of a parent record
    parent_naid = "1667751"
    
    try:
        children = client.get_child_records(parent_naid)
        
        child_count = len(children.get('results', {}).get('result', []))
        print(f"\nFound {child_count} child records for NAID {parent_naid}")
        
        if child_count > 0:
            print("\nChild records:")
            for child in children['results']['result'][:5]:
                print(f"  • {child.get('title')} (NAID: {child.get('naId')})")
    except Exception as e:
        print(f"\nNo child records or error: {e}")


def example_with_caching():
    """Example: Using cache for efficiency."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Response Caching")
    print("=" * 60)
    
    import time
    
    cache_dir = Path("cache/nara-example")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    client = NARAAPIClient(cache_dir=str(cache_dir))
    
    # First request (hits API)
    print("\nFirst request (will cache)...")
    start = time.time()
    results1 = client.search_records(query="declaration", rows=1)
    time1 = time.time() - start
    print(f"Time: {time1:.3f}s")
    
    # Second request (uses cache)
    print("\nSecond request (from cache)...")
    start = time.time()
    results2 = client.search_records(query="declaration", rows=1)
    time2 = time.time() - start
    print(f"Time: {time2:.3f}s")
    
    print(f"\nSpeedup: {time1/time2:.1f}x faster")
    
    # Cleanup
    client.clear_cache()
    
    if cache_dir.exists():
        cache_dir.rmdir()


def example_batch_fetch():
    """Example: Fetching multiple documents."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Batch Document Fetch")
    print("=" * 60)
    
    from scripts.fetch_founding_documents import DocumentFetcher, FOUNDING_DOCUMENTS
    
    fetcher = DocumentFetcher()
    
    print("\nFetching founding documents...")
    
    # Fetch just Constitution and Bill of Rights
    docs_to_fetch = ['constitution', 'bill-of-rights']
    
    for doc_key in docs_to_fetch:
        doc_info = FOUNDING_DOCUMENTS[doc_key]
        print(f"\nFetching: {doc_info['title']}")
        success = fetcher.fetch_document(doc_key, doc_info)
        
        if success:
            print(f"  ✅ Success")
        else:
            print(f"  ❌ Failed")
    
    print(f"\nTotal fetched: {fetcher.fetched_count}")
    print(f"Total failed: {fetcher.failed_count}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("NATIONAL ARCHIVES API - INTEGRATION EXAMPLES")
    print("=" * 60)
    
    try:
        # Check if API key is configured
        if not os.getenv('NARA_API_KEY'):
            print("\n❌ Error: NARA_API_KEY not set")
            print("Please set your API key in the .env file")
            return 1
        
        # Run examples
        examples = [
            example_basic_search,
            example_get_specific_document,
            example_get_transcription,
            example_get_extracted_text,
            example_search_with_filters,
            example_get_child_records,
            example_with_caching,
            example_batch_fetch,
        ]
        
        for example in examples:
            try:
                example()
            except Exception as e:
                print(f"\n❌ Example failed: {e}")
        
        print("\n" + "=" * 60)
        print("Examples complete!")
        print("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130


if __name__ == '__main__':
    sys.exit(main())
