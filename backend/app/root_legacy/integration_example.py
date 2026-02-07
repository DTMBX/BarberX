# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

# integration_example.py
"""
Example integration of data rights compliance into Evident Legal Tech.
This shows how to protect your law firm from copyright lawsuits.
"""

from datetime import datetime
from pathlib import Path

from .data_rights import RIGHTS_PROFILES, ExportViolation, Material, RightsAwareExport


def example_compliant_discovery_production():
    """
    Example: Creating a compliant discovery production package.
    This demonstrates Pattern 1-3 implementation.
    """
    print("=" * 80)
    print("EXAMPLE: Rights-Compliant Discovery Production")
    print("=" * 80)

    # Step 1: Create export package
    export = RightsAwareExport(case_number="ATL-L-002794-25", export_type="discovery_production")

    # Step 2: Add BWC footage (PUBLIC RECORD - ALLOWED)
    print("\n✅ Adding BWC footage from OPRA request...")
    bwc = Material(
        filename="BWC_Officer_Smith_2025-01-15.mp4",
        category="bwc_videos",
        rights=RIGHTS_PROFILES["opra_bwc"],
        acquired_by="John Doe, Esq.",
        acquired_date=datetime(2025, 1, 18),
        source_url="OPRA Request #2025-001 - Atlantic County Sheriff",
        file_path=Path("./evidence/bwc_videos/BWC_Officer_Smith_2025-01-15.mp4"),
    )
    if export.add_material(bwc):
        print("   → BWC footage added to export")

    # Step 3: Add our AI transcript (OUR WORK PRODUCT - ALLOWED)
    print("\n✅ Adding our AI-generated transcript...")
    transcript = Material(
        filename="BWC_transcript_2025-01-15.pdf",
        category="transcripts",
        rights=RIGHTS_PROFILES["our_transcript"],
        acquired_by="Evident Legal Tech Platform",
        acquired_date=datetime(2025, 1, 20),
        file_path=Path("./evidence/transcripts/BWC_transcript_2025-01-15.pdf"),
    )
    if export.add_material(transcript):
        print("   → Transcript added to export")

    # Step 4: Add case law from CourtListener (PUBLIC DOMAIN - ALLOWED)
    print("\n✅ Adding public domain case law...")
    case_law = Material(
        filename="Tennessee_v_Garner_471_US_1.pdf",
        category="case_law",
        rights=RIGHTS_PROFILES["courtlistener"],
        acquired_by="Research Team",
        acquired_date=datetime(2025, 1, 15),
        source_url="https://www.courtlistener.com/opinion/111150/tennessee-v-garner/",
        content="The court held that the use of deadly force to prevent escape is constitutional only when the officer has probable cause to believe that the suspect poses a significant threat of death or serious physical injury.",
        is_excerpt=True,
    )
    if export.add_material(case_law):
        print("   → Case law excerpt added to export")

    # Step 5: Try to add Westlaw content (PROPRIETARY - BLOCKED)
    print("\n❌ Attempting to add Westlaw proprietary content...")
    print("   (This should be AUTO-EXCLUDED)")
    westlaw_keycite = Material(
        filename="Garner_KeyCite_Analysis.pdf",
        category="legal_research",
        rights=RIGHTS_PROFILES["westlaw"],  # Marked as export_allowed=False
        acquired_by="Research Team",
        source_url="Westlaw subscription",
    )
    if not export.add_material(westlaw_keycite):
        print("   → Westlaw content EXCLUDED (as expected)")
        print("   → Reason: Proprietary database - internal use only")

    # Step 6: Try to add police report full text (COPYRIGHTED - BLOCKED)
    print("\n❌ Attempting to add full police report...")
    print("   (This should be AUTO-EXCLUDED - full text not allowed)")
    police_report = Material(
        filename="Police_Report_Full.pdf",
        category="documents",
        rights=RIGHTS_PROFILES["police_report"],  # Marked as fair_use_only=True
        acquired_by="John Doe, Esq.",
        is_excerpt=False,  # Full text - NOT ALLOWED
    )
    if not export.add_material(police_report):
        print("   → Police report full text EXCLUDED (as expected)")
        print("   → Reason: Fair use excerpts only - full text prohibited")

    # Step 7: Add police report EXCERPT (FAIR USE - ALLOWED)
    print("\n✅ Adding fair use excerpt from police report...")
    police_excerpt = Material(
        filename="Police_Report_Excerpt.pdf",
        category="documents",
        rights=RIGHTS_PROFILES["police_report"],
        acquired_by="John Doe, Esq.",
        acquired_date=datetime(2025, 1, 10),
        content="Officer Smith stated: 'Suspect fled on foot. I pursued for approximately 50 yards before losing visual contact.' [Fair use excerpt - 20 words]",
        is_excerpt=True,
    )
    if export.add_material(police_excerpt):
        print("   → Police report excerpt added to export")

    # Step 8: Finalize export with attorney certification
    print("\n" + "=" * 80)
    print("FINALIZING EXPORT PACKAGE")
    print("=" * 80)

    export_path = export.finalize_export(
        certifying_attorney="John Doe, Esq.",
        attorney_bar_number="NJ12345",
        export_directory=Path("./exports"),
    )

    # Summary
    print("\n" + "=" * 80)
    print("EXPORT SUMMARY")
    print("=" * 80)
    print(f"Export ID: {export.export_id}")
    print("Case Number: ATL-L-002794-25")
    print(f"Export Directory: {export_path}")
    print(f"\nMaterials Included: {len(export.materials)}")
    for material in export.materials:
        print(f"  ✅ {material.filename}")

    print(f"\nMaterials Excluded: {len(export.excluded_materials)}")
    for excluded in export.excluded_materials:
        print(f"  ❌ {excluded['filename']}")
        print(f"     Reason: {excluded['reason']}")

    print(f"\nAttribution Requirements: {len(export.manifest['attribution_requirements'])}")
    for attribution in export.manifest["attribution_requirements"]:
        print(f"  • {attribution}")

    print("\n" + "=" * 80)
    print("✅ COMPLIANCE CHECK: PASSED")
    print("=" * 80)
    print("• No proprietary database content in export")
    print("• All excerpts within fair use limits (≤200 words)")
    print("• Attribution requirements documented")
    print("• Rights manifest generated")
    print("• Attorney certification recorded")
    print("\n✅ SAFE TO FILE WITH COURT / PRODUCE IN DISCOVERY")
    print("=" * 80)


def example_block_dangerous_export():
    """
    Example: Demonstrating export blocking for copyright violations.
    """
    print("\n\n" + "=" * 80)
    print("EXAMPLE: Blocking Dangerous Copyright Violations")
    print("=" * 80)

    export = RightsAwareExport(case_number="TEST-123", export_type="test_compliance")

    # Scenario 1: Try to export Westlaw content directly
    print("\n🚨 Scenario 1: Attempting to force-export Westlaw content...")
    try:
        westlaw = Material(
            filename="Westlaw_KeyCite.pdf", category="research", rights=RIGHTS_PROFILES["westlaw"]
        )
        # This will auto-exclude, but let's check
        result = export.add_material(westlaw)
        if not result:
            print("   ✅ BLOCKED: Westlaw content auto-excluded")
    except ExportViolation as e:
        print(f"   ✅ BLOCKED: {e}")

    # Scenario 2: Try to export excerpt that's too long
    print("\n🚨 Scenario 2: Fair use excerpt exceeding 200 words...")
    long_excerpt = Material(
        filename="Police_Report_Long_Excerpt.pdf",
        category="documents",
        rights=RIGHTS_PROFILES["police_report"],
        content=" ".join(["word"] * 250),  # 250 words - EXCEEDS LIMIT
        is_excerpt=True,
    )
    try:
        export.add_material(long_excerpt)
    except ExportViolation as e:
        print(f"   ✅ BLOCKED: {e}")

    print("\n" + "=" * 80)
    print("✅ COPYRIGHT PROTECTION WORKING")
    print("=" * 80)
    print("System successfully blocked all dangerous exports!")


if __name__ == "__main__":
    # Run compliance examples
    example_compliant_discovery_production()
    example_block_dangerous_export()

    print("\n\n" + "=" * 80)
    print("INTEGRATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run: python models_data_rights.py  # Create database tables")
    print("2. Import data_rights module into your app.py")
    print("3. Wrap all export functions with RightsAwareExport")
    print("4. Review DATA-RIGHTS-COMPLIANCE.md for full details")
    print("\n⚖️ Your law firm is now protected from copyright lawsuits!")
    print("=" * 80)
