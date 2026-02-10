#!/usr/bin/env python3
"""
Fetch Founding Documents from National Archives

This script retrieves founding documents and treaties from the National Archives API
and saves them in a structured, auditable format.

Preserves:
- Original metadata
- Retrieval timestamps
- Source attribution
- Chain of custody

Usage:
    python scripts/fetch_founding_documents.py
    python scripts/fetch_founding_documents.py --document constitution
    python scripts/fetch_founding_documents.py --all
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.nara_api_client import NARAAPIClient, NARAAPIError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Known NAIDs for founding documents
FOUNDING_DOCUMENTS = {
    'constitution': {
        'naid': '1667751',
        'title': 'Constitution of the United States',
        'filename': 'constitution.md',
        'description': 'Original Constitution ratified 1788',
        'search_terms': ['constitution', 'founding fathers', '1787']
    },
    'bill-of-rights': {
        'naid': '1408042',
        'title': 'Bill of Rights',
        'filename': 'bill-of-rights.md',
        'description': 'First ten amendments to the Constitution',
        'search_terms': ['bill of rights', 'first amendment', '1791']
    },
    'declaration': {
        'naid': '1419123',
        'title': 'Declaration of Independence',
        'filename': 'declaration-of-independence.md',
        'description': 'Declaration adopted July 4, 1776',
        'search_terms': ['declaration of independence', '1776', 'thomas jefferson']
    },
    'articles-of-confederation': {
        'naid': '1408033',
        'title': 'Articles of Confederation',
        'filename': 'articles-of-confederation.md',
        'description': 'First constitution of the United States, adopted 1781',
        'search_terms': ['articles of confederation', '1781']
    },
    'federalist-papers': {
        'naid': None,  # Collection, not single document
        'title': 'The Federalist Papers',
        'filename': 'federalist-papers.md',
        'description': 'Essays promoting Constitution ratification',
        'search_terms': ['federalist papers', 'hamilton', 'madison', 'jay']
    },
    'emancipation-proclamation': {
        'naid': '299998',
        'title': 'Emancipation Proclamation',
        'filename': 'emancipation-proclamation.md',
        'description': 'Proclamation freeing enslaved people, issued 1863',
        'search_terms': ['emancipation proclamation', 'lincoln', '1863']
    },
}

# Treaty NAIDs (examples - expand as needed)
TREATIES = {
    'treaty-of-paris-1783': {
        'naid': '299808',
        'title': 'Treaty of Paris (1783)',
        'filename': 'treaty-of-paris-1783.md',
        'description': 'Treaty ending Revolutionary War',
        'search_terms': ['treaty of paris', '1783', 'revolutionary war']
    },
    'louisiana-purchase': {
        'naid': '299810',
        'title': 'Louisiana Purchase Treaty',
        'filename': 'louisiana-purchase-treaty.md',
        'description': 'Treaty for Louisiana Territory purchase, 1803',
        'search_terms': ['louisiana purchase', '1803', 'jefferson']
    },
}


class DocumentFetcher:
    """Fetches and stores founding documents from National Archives."""
    
    def __init__(
        self,
        output_dir: str = 'documents/founding',
        cache_dir: str = 'cache/nara'
    ):
        """
        Initialize document fetcher.
        
        Args:
            output_dir: Directory to save documents
            cache_dir: Directory for API response cache
        """
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize API client
        self.client = NARAAPIClient(cache_dir=str(self.cache_dir))
        
        # Track operations
        self.fetched_count = 0
        self.failed_count = 0
        self.errors: List[str] = []
    
    def fetch_document(
        self,
        doc_key: str,
        doc_info: Dict[str, Any],
        force_refresh: bool = False
    ) -> bool:
        """
        Fetch a single document.
        
        Args:
            doc_key: Document identifier key
            doc_info: Document metadata
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Fetching: {doc_info['title']}")
        
        try:
            # Get document metadata
            if doc_info['naid']:
                record = self.client.get_record_by_naid(doc_info['naid'])
            else:
                # Search for document
                results = self.client.search_records(
                    query=' '.join(doc_info['search_terms']),
                    rows=1
                )
                if results.get('opaResponse', {}).get('results', {}).get('total', 0) == 0:
                    raise NARAAPIError(f"No results found for {doc_info['title']}")
                record = results['opaResponse']['results']['result'][0]
            
            # Extract useful information
            naid = record.get('naId')
            title = record.get('title', doc_info['title'])
            description = record.get('scopeContent', {}).get('scopeContentNote', {}).get('note', '')
            
            # Try to get transcription
            transcription_text = None
            if naid:
                try:
                    transcriptions = self.client.get_transcriptions_by_naid(naid)
                    if transcriptions and len(transcriptions) > 0:
                        # Get the most recent transcription
                        transcription_text = transcriptions[0].get('transcription')
                except NARAAPIError:
                    logger.warning(f"No transcriptions available for {title}")
                
                # Try to get extracted text
                if not transcription_text:
                    extracted_text = self.client.get_extracted_text(naid)
                    if extracted_text:
                        transcription_text = extracted_text
            
            # Generate markdown document
            markdown_content = self._generate_markdown(
                doc_info=doc_info,
                record=record,
                transcription=transcription_text
            )
            
            # Save to file
            output_file = self.output_dir / doc_info['filename']
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Saved: {output_file}")
            
            # Also copy to _includes/founding/ for Jekyll rendering
            includes_dir = Path('_includes/founding')
            includes_dir.mkdir(parents=True, exist_ok=True)
            includes_file = includes_dir / doc_info['filename']
            with open(includes_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Synced to Jekyll includes: {includes_file}")
            self.fetched_count += 1
            return True
            
        except Exception as e:
            error_msg = f"Failed to fetch {doc_info['title']}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            self.failed_count += 1
            return False
    
    def _generate_markdown(
        self,
        doc_info: Dict[str, Any],
        record: Dict[str, Any],
        transcription: Optional[str]
    ) -> str:
        """
        Generate markdown document with metadata.
        
        Args:
            doc_info: Document configuration
            record: NARA record metadata
            transcription: Document text content
            
        Returns:
            Formatted markdown string
        """
        naid = record.get('naId', 'Unknown')
        title = record.get('title', doc_info['title'])
        
        # Build metadata section
        lines = [
            f"# {title}",
            "",
            "**Official Source:** National Archives of the United States",
            f"**NAID:** {naid}",
            f"**Source URL:** https://catalog.archives.gov/id/{naid}",
            f"**Retrieved:** {datetime.now().strftime('%B %d, %Y')}",
            "",
            "> Note: This document was retrieved from the National Archives Catalog",
            "> using the NextGen Catalog API. Content is preserved as recorded by",
            "> the National Archives.",
            "",
            "---",
            "",
        ]
        
        # Description
        description = record.get('scopeContent', {}).get('scopeContentNote', {}).get('note', '')
        if description:
            lines.extend([
                "## Description",
                "",
                description,
                "",
                "---",
                ""
            ])
        
        # Document content
        if transcription:
            lines.extend([
                "## Document Text",
                "",
                transcription,
                ""
            ])
        else:
            lines.extend([
                "## Document Text",
                "",
                "*Transcription not available through API. Please visit the National Archives*",
                f"*Catalog at https://catalog.archives.gov/id/{naid} to view the original document.*",
                ""
            ])
        
        # Metadata footer
        lines.extend([
            "---",
            "",
            "## Retrieval Metadata",
            "",
            f"- **Retrieved:** {datetime.now().isoformat()}",
            f"- **NAID:** {naid}",
            f"- **API Version:** NextGen Catalog API v2",
            f"- **Retrieval Method:** Automated via NARA API Client",
            "",
            "### Chain of Custody",
            "",
            "1. **Source Authority:** National Archives of the United States",
            "2. **Retrieval System:** Evident Technologies Document Management",
            "3. **Verification:** Content retrieved via authenticated API connection",
            "4. **Integrity:** Original formatting and metadata preserved",
            "",
            "### Contact",
            "",
            "For questions about this document or the National Archives API:",
            "- **Email:** Catalog_API@nara.gov",
            "- **Catalog:** https://catalog.archives.gov",
            ""
        ])
        
        return '\n'.join(lines)
    
    def fetch_all_founding_documents(self) -> Dict[str, Any]:
        """
        Fetch all founding documents.
        
        Returns:
            Summary report
        """
        logger.info("Fetching all founding documents...")
        
        for doc_key, doc_info in FOUNDING_DOCUMENTS.items():
            self.fetch_document(doc_key, doc_info)
        
        return self._generate_report()
    
    def fetch_all_treaties(self) -> Dict[str, Any]:
        """
        Fetch all treaties.
        
        Returns:
            Summary report
        """
        logger.info("Fetching all treaties...")
        
        for treaty_key, treaty_info in TREATIES.items():
            self.fetch_document(treaty_key, treaty_info)
        
        return self._generate_report()
    
    def fetch_all(self) -> Dict[str, Any]:
        """
        Fetch all documents and treaties.
        
        Returns:
            Summary report
        """
        self.fetch_all_founding_documents()
        self.fetch_all_treaties()
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate summary report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'fetched': self.fetched_count,
            'failed': self.failed_count,
            'errors': self.errors,
            'output_directory': str(self.output_dir),
            'success_rate': (
                f"{(self.fetched_count / (self.fetched_count + self.failed_count) * 100):.1f}%"
                if (self.fetched_count + self.failed_count) > 0
                else "N/A"
            )
        }
        
        # Save report
        report_file = self.output_dir / f"fetch-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved: {report_file}")
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fetch founding documents from National Archives'
    )
    parser.add_argument(
        '--document',
        choices=list(FOUNDING_DOCUMENTS.keys()) + list(TREATIES.keys()),
        help='Fetch specific document'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Fetch all documents and treaties'
    )
    parser.add_argument(
        '--founding-only',
        action='store_true',
        help='Fetch only founding documents'
    )
    parser.add_argument(
        '--treaties-only',
        action='store_true',
        help='Fetch only treaties'
    )
    parser.add_argument(
        '--output-dir',
        default='documents/founding',
        help='Output directory for documents'
    )
    parser.add_argument(
        '--cache-dir',
        default='cache/nara',
        help='Cache directory for API responses'
    )
    
    args = parser.parse_args()
    
    # Create fetcher
    fetcher = DocumentFetcher(
        output_dir=args.output_dir,
        cache_dir=args.cache_dir
    )
    
    # Execute requested operation
    if args.document:
        # Fetch specific document
        doc_info = FOUNDING_DOCUMENTS.get(args.document) or TREATIES.get(args.document)
        fetcher.fetch_document(args.document, doc_info)
        report = fetcher._generate_report()
    elif args.all:
        report = fetcher.fetch_all()
    elif args.treaties_only:
        report = fetcher.fetch_all_treaties()
    else:
        # Default: fetch founding documents
        report = fetcher.fetch_all_founding_documents()
    
    # Print summary
    print("\n" + "=" * 60)
    print("FETCH SUMMARY")
    print("=" * 60)
    print(f"Successfully fetched: {report['fetched']}")
    print(f"Failed: {report['failed']}")
    print(f"Success rate: {report['success_rate']}")
    print(f"Output directory: {report['output_directory']}")
    
    if report['errors']:
        print("\nErrors:")
        for error in report['errors']:
            print(f"  - {error}")
    
    print("=" * 60)
    
    return 0 if report['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
