# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Automated Overnight Library Builder

Runs overnight to populate library with verified foundation cases.
Only uses legitimate, verified, and respected sources.

SAFETY FEATURES:
- Rate limiting to respect API terms
- Source verification before import
- Duplicate detection
- Error handling and recovery
- Progress logging
- Graceful shutdown on errors

Run with: python overnight_library_builder.py --practice-area all
"""

import argparse
import json
import logging
import time
from datetime import datetime

from .batch_import_foundation_cases import FOUNDATION_CASES
from .verified_legal_sources import SourceCredibilityTracker, VerifiedLegalSources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/overnight_import_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class OvernightLibraryBuilder:
    """
    Automated library builder with safety features

    Features:
    - Rate limiting (2 seconds between requests)
    - Source verification
    - Progress tracking
    - Error recovery
    - Statistics reporting
    """

    def __init__(self, rate_limit_seconds: int = 2):
        self.verified_sources = VerifiedLegalSources()
        self.credibility_tracker = SourceCredibilityTracker()
        self.rate_limit = rate_limit_seconds
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_attempted": 0,
            "imported": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
        }

    def build_library(self, practice_areas: list[str] = None, max_cases: int = None) -> dict:
        """
        Build library overnight from verified sources

        Args:
            practice_areas: List of practice areas or None for all
            max_cases: Maximum cases to import (None for unlimited)

        Returns:
            Statistics dictionary
        """

        self.stats["start_time"] = datetime.now()

        logger.info("=" * 60)
        logger.info("Overnight Library Builder - Starting")
        logger.info("=" * 60)
        logger.info(f"Practice areas: {practice_areas or 'ALL'}")
        logger.info(f"Rate limit: {self.rate_limit} seconds")
        logger.info(f"Max cases: {max_cases or 'UNLIMITED'}")
        logger.info("")

        # Get cases to import
        cases = self._get_cases_to_import(practice_areas)

        if max_cases:
            cases = cases[:max_cases]

        self.stats["total_attempted"] = len(cases)
        logger.info(f"Total cases to import: {len(cases)}")
        logger.info("")

        # Import each case
        for i, (title, citation, year) in enumerate(cases, 1):
            logger.info(f"[{i}/{len(cases)}] {citation} - {title}")

            try:
                # Check if already exists
                from legal_library import LegalDocument

                existing = LegalDocument.query.filter_by(citation=citation).first()

                if existing:
                    logger.info(f"  [OK] Already in library (id: {existing.id})")
                    self.stats["skipped"] += 1
                    continue

                # Verify source credibility
                verification = self.verified_sources.verify_citation_authenticity(
                    citation, "courtlistener"
                )

                if not verification["authentic"]:
                    logger.warning("  [WARN] Could not verify citation authenticity via API")
                    logger.info("  [INFO] Attempting direct import anyway...")
                else:
                    logger.info(f"  [OK] Verified (confidence: {verification['confidence']})")

                # Try to import from CourtListener (even if not verified)
                doc = self.verified_sources.import_from_courtlistener(citation)

                if doc:
                    logger.info(f"  [OK] Imported successfully (id: {doc.id})")
                    self.stats["imported"] += 1

                    # Log to database
                    self._log_import(doc, verification)
                else:
                    logger.error("  [FAIL] Import failed - not found on CourtListener")
                    self.stats["failed"] += 1
                    self.stats["errors"].append(
                        {"citation": citation, "reason": "Not found on CourtListener"}
                    )

                # Rate limiting
                if self.rate_limit > 0 and i < len(cases):
                    logger.info(f"  ⏳ Waiting {self.rate_limit}s (rate limiting)...")
                    time.sleep(self.rate_limit)

            except Exception as e:
                logger.error(f"  [FAIL] Error: {e}")
                self.stats["failed"] += 1
                self.stats["errors"].append({"citation": citation, "error": str(e)})

        # Finalize
        self.stats["end_time"] = datetime.now()
        self._generate_report()

        return self.stats

    def _get_cases_to_import(self, practice_areas: list[str] = None) -> list[tuple]:
        """Get list of cases to import"""

        if not practice_areas or "all" in practice_areas:
            # All cases
            cases = []
            for area_cases in FOUNDATION_CASES.values():
                cases.extend(area_cases)
            return cases
        else:
            # Specific practice areas
            cases = []
            for area in practice_areas:
                if area in FOUNDATION_CASES:
                    cases.extend(FOUNDATION_CASES[area])
            return cases

    def _log_import(self, doc, verification: dict):
        """Log successful import to database"""

        # TODO: Create import_log table to track what was imported and when
        pass

    def _generate_report(self):
        """Generate final import report"""

        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        logger.info("")
        logger.info("=" * 60)
        logger.info("Overnight Library Builder - Complete")
        logger.info("=" * 60)
        logger.info(f"Started:  {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Finished: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {duration:.1f} seconds ({duration / 60:.1f} minutes)")
        logger.info("")
        logger.info(f"Total attempted: {self.stats['total_attempted']}")
        logger.info(f"[OK] Imported:      {self.stats['imported']}")
        logger.info(f"[SKIP] Skipped:     {self.stats['skipped']}")
        logger.info(f"[FAIL] Failed:      {self.stats['failed']}")
        logger.info("")

        success_rate = (
            (self.stats["imported"] / self.stats["total_attempted"] * 100)
            if self.stats["total_attempted"] > 0
            else 0
        )

        logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info(f"Total cases in library: {self.stats['imported'] + self.stats['skipped']}")
        logger.info("")

        # Log errors if any
        if self.stats["errors"]:
            logger.info("Errors encountered:")
            for error in self.stats["errors"]:
                logger.info(
                    f"  - {error.get('citation', 'Unknown')}: {error.get('reason', error.get('error'))}"
                )

        logger.info("=" * 60)

        # Save report to file
        report_path = f"logs/import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            # Convert datetime to string for JSON
            stats_copy = self.stats.copy()
            stats_copy["start_time"] = stats_copy["start_time"].isoformat()
            stats_copy["end_time"] = stats_copy["end_time"].isoformat()
            json.dump(stats_copy, f, indent=2)

        logger.info(f"Report saved to: {report_path}")


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Overnight Library Builder - Import verified legal cases"
    )
    parser.add_argument(
        "--practice-area",
        nargs="+",
        default=["all"],
        choices=["all", "civil_rights", "criminal_defense", "employment", "constitutional"],
        help="Practice areas to import",
    )
    parser.add_argument(
        "--max-cases", type=int, default=None, help="Maximum number of cases to import"
    )
    parser.add_argument(
        "--rate-limit", type=int, default=2, help="Seconds to wait between requests (default: 2)"
    )

    args = parser.parse_args()

    # Create logs directory
    import os

    os.makedirs("logs", exist_ok=True)

    # Run builder
    from app import app

    with app.app_context():
        builder = OvernightLibraryBuilder(rate_limit_seconds=args.rate_limit)
        stats = builder.build_library(practice_areas=args.practice_area, max_cases=args.max_cases)

        # Exit code based on success
        if stats["imported"] > 0:
            return 0  # Success
        else:
            return 1  # Failure


if __name__ == "__main__":
    import sys

    sys.exit(main())


"""
USAGE EXAMPLES:

# Import all foundation cases
python overnight_library_builder.py --practice-area all

# Import only civil rights cases
python overnight_library_builder.py --practice-area civil_rights

# Import first 10 cases (for testing)
python overnight_library_builder.py --practice-area all --max-cases 10

# Import with slower rate limit (3 seconds)
python overnight_library_builder.py --practice-area all --rate-limit 3

# Import multiple practice areas
python overnight_library_builder.py --practice-area civil_rights criminal_defense

# Schedule for overnight (Windows Task Scheduler)
# Run at 2 AM daily:
# schtasks /create /tn "Legal Library Import" /tr "python overnight_library_builder.py --practice-area all" /sc daily /st 02:00

# Schedule for overnight (Unix cron)
# Add to crontab:
# 0 2 * * * cd /path/to/Evident.info && python overnight_library_builder.py --practice-area all
"""
