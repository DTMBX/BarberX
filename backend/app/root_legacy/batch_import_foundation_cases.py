"""
Batch Import Foundation Cases

Imports essential case law for common practice areas:
- Civil Rights / Police Misconduct
- Criminal Defense
- Employment Law
- Constitutional Law

Run with: python batch_import_foundation_cases.py
"""

import time
from datetime import datetime

from legal_library import LegalLibraryService

# Foundation cases for different practice areas
FOUNDATION_CASES = {
    "civil_rights": [
        # Supreme Court - Civil Rights
        ("Miranda v. Arizona", "384 U.S. 436", "1966"),
        ("Terry v. Ohio", "392 U.S. 1", "1968"),
        ("Tennessee v. Garner", "471 U.S. 1", "1985"),
        ("Graham v. Connor", "490 U.S. 386", "1989"),
        ("Monell v. Department of Social Services", "436 U.S. 658", "1978"),
        ("Payton v. New York", "445 U.S. 573", "1980"),
        ("Mapp v. Ohio", "367 U.S. 643", "1961"),
        ("Katz v. United States", "389 U.S. 347", "1967"),
        ("Chimel v. California", "395 U.S. 752", "1969"),
        ("United States v. Wade", "388 U.S. 218", "1967"),
    ],
    "criminal_defense": [
        # Supreme Court - Criminal Defense
        ("Gideon v. Wainwright", "372 U.S. 335", "1963"),
        ("Brady v. Maryland", "373 U.S. 83", "1963"),
        ("Batson v. Kentucky", "476 U.S. 79", "1986"),
        ("Giglio v. United States", "405 U.S. 150", "1972"),
        ("Kyles v. Whitley", "514 U.S. 419", "1995"),
        ("Strickland v. Washington", "466 U.S. 668", "1984"),
        ("Crawford v. Washington", "541 U.S. 36", "2004"),
        ("Berghuis v. Thompkins", "560 U.S. 370", "2010"),
    ],
    "employment": [
        # Supreme Court - Employment Law
        ("McDonnell Douglas Corp. v. Green", "411 U.S. 792", "1973"),
        ("Burlington Industries v. Ellerth", "524 U.S. 742", "1998"),
        ("Faragher v. City of Boca Raton", "524 U.S. 775", "1998"),
        ("Harris v. Forklift Systems", "510 U.S. 17", "1993"),
        ("Price Waterhouse v. Hopkins", "490 U.S. 228", "1989"),
    ],
    "constitutional": [
        # Landmark Constitutional Cases
        ("Brown v. Board of Education", "347 U.S. 483", "1954"),
        ("Roe v. Wade", "410 U.S. 113", "1973"),
        ("Marbury v. Madison", "5 U.S. 137", "1803"),
        ("McCulloch v. Maryland", "17 U.S. 316", "1819"),
    ],
}


def import_foundation_library(practice_area: str = "all", delay_seconds: int = 2):
    """
    Import foundation cases for specified practice area

    Args:
        practice_area: 'all', 'civil_rights', 'criminal_defense', 'employment', 'constitutional'
        delay_seconds: Delay between requests to avoid rate limiting
    """

    library = LegalLibraryService()

    # Determine which cases to import
    if practice_area == "all":
        cases_to_import = []
        for area_cases in FOUNDATION_CASES.values():
            cases_to_import.extend(area_cases)
    else:
        cases_to_import = FOUNDATION_CASES.get(practice_area, [])

    print(f"Importing {len(cases_to_import)} foundation cases...")
    print(f"Practice area: {practice_area}")
    print(f"Delay between requests: {delay_seconds} seconds\n")

    imported = 0
    skipped = 0
    failed = 0

    for title, citation, year in cases_to_import:
        print(f"Importing: {citation} - {title}")

        try:
            # Check if already exists
            from legal_library import LegalDocument
            from models_auth import db

            existing = LegalDocument.query.filter_by(citation=citation).first()

            if existing:
                print(f"  ✓ Already in library (id: {existing.id})")
                skipped += 1
                continue

            # Import from CourtListener
            doc = library.ingest_from_courtlistener(citation)

            if doc:
                print(f"  ✓ Imported successfully (id: {doc.id})")
                imported += 1
            else:
                print(f"  ✗ Import failed - not found on CourtListener")
                failed += 1

            # Delay to avoid rate limiting
            if delay_seconds > 0:
                time.sleep(delay_seconds)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Import Complete!")
    print(f"{'='*60}")
    print(f"✓ Imported: {imported}")
    print(f"⊙ Skipped (already in library): {skipped}")
    print(f"✗ Failed: {failed}")
    print(f"Total cases in library: {imported + skipped}")


def import_custom_cases(citations: list, delay_seconds: int = 2):
    """
    Import custom list of citations

    Args:
        citations: List of citation strings (e.g., ["384 U.S. 436", "392 U.S. 1"])
        delay_seconds: Delay between requests
    """

    library = LegalLibraryService()

    print(f"Importing {len(citations)} custom cases...\n")

    imported = 0
    failed = 0

    for citation in citations:
        print(f"Importing: {citation}")

        try:
            doc = library.ingest_from_courtlistener(citation)

            if doc:
                print(f"  ✓ {doc.title} (id: {doc.id})")
                imported += 1
            else:
                print(f"  ✗ Not found")
                failed += 1

            if delay_seconds > 0:
                time.sleep(delay_seconds)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    print(f"\nImported {imported}/{len(citations)} cases")


if __name__ == "__main__":
    import sys

    from app import app

    # Run in Flask app context
    with app.app_context():

        if len(sys.argv) > 1:
            practice_area = sys.argv[1]
        else:
            practice_area = "all"

        # Import foundation library
        import_foundation_library(practice_area, delay_seconds=2)

        print("\n" + "=" * 60)
        print("Foundation library import complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Search library: GET /api/legal-library/search?q=miranda")
        print("2. View document: GET /api/legal-library/document/1")
        print("3. Add annotations: POST /api/legal-library/annotate")
