# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Evident BWC Analysis - Discovery Files Test
Tests real BWC footage analysis with Devon T. Barber case files
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("?? Evident BWC Analysis - Discovery Files Test")
print("=" * 60)

# Discovery folder
DISCOVERY_PATH = Path("assets/discovery/25-41706 Barber, Devon")

# Check if BWC analyzer is available
try:
    from bwc_forensic_analyzer import BWCForensicAnalyzer

    print("? BWC Forensic Analyzer module loaded")
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"??  BWC Analyzer not available: {e}")
    print("   AI dependencies not installed. Testing file structure only.")
    ANALYZER_AVAILABLE = False

# List all BWC files
print(f"\n?? Discovery Folder: {DISCOVERY_PATH}")

if not DISCOVERY_PATH.exists():
    print(f"? Discovery folder not found: {DISCOVERY_PATH}")
    sys.exit(1)

# Find all MP4 files
bwc_files = list(DISCOVERY_PATH.glob("*.mp4")) + list(DISCOVERY_PATH.glob("*.mov"))
bwc_files.sort()

print(f"\n?? Found {len(bwc_files)} BWC video files:")
print("-" * 60)

total_size = 0
for i, file in enumerate(bwc_files, 1):
    size_mb = file.stat().st_size / (1024 * 1024)
    total_size += size_mb
    duration = "Unknown"

    # Parse filename for officer and timestamp
    filename = file.stem
    parts = filename.split("_")
    officer = parts[0] if parts else "Unknown"
    timestamp = parts[1] if len(parts) > 1 else "Unknown"
    device = parts[2] if len(parts) > 2 else "Unknown"

    print(f"{i:2d}. {file.name}")
    print(f"    Officer: {officer}")
    print(f"    Timestamp: {timestamp}")
    print(f"    Device: {device}")
    print(f"    Size: {size_mb:,.1f} MB")
    print()

print(f"?? Total footage: {total_size:,.1f} MB ({total_size / 1024:.2f} GB)")
print(f"?? Total files: {len(bwc_files)}")

# Group by officer
officers = {}
for file in bwc_files:
    parts = file.stem.split("_")
    officer = parts[0] if parts else "Unknown"
    if officer not in officers:
        officers[officer] = []
    officers[officer].append(file)

print("\n?? Officers with BWC footage:")
print("-" * 60)
for officer, files in sorted(officers.items()):
    total_officer_size = sum(f.stat().st_size / (1024 * 1024) for f in files)
    print(f"{officer}: {len(files)} files ({total_officer_size:,.1f} MB)")

# Test analysis on smallest file (for speed)
if ANALYZER_AVAILABLE and bwc_files:
    print("\n" + "=" * 60)
    print("?? TESTING BWC ANALYSIS")
    print("=" * 60)

    # Use smallest file for quick test
    smallest_file = min(bwc_files, key=lambda f: f.stat().st_size)
    size_mb = smallest_file.stat().st_size / (1024 * 1024)

    print(f"\n?? Analyzing: {smallest_file.name}")
    print(f"   Size: {size_mb:.1f} MB")
    print("   This may take 2-5 minutes...\n")

    try:
        # Initialize analyzer
        print("?? Initializing BWC Analyzer...")
        analyzer = BWCForensicAnalyzer(
            whisper_model_size="tiny",
            hf_token=os.getenv("HUGGINGFACE_TOKEN"),  # Use tiny for speed
        )

        # Establish chain of custody
        print("?? Establishing chain of custody...")
        custody = analyzer.establish_chain_of_custody(
            file_path=str(smallest_file),
            acquired_by="Devon T. Barber",
            source="Discovery production - Case 25-41706",
        )

        print(f"   ? SHA-256 Hash: {custody.sha256_hash}")
        print(f"   ? File size: {custody.file_size:,} bytes")
        print(f"   ? Acquired: {custody.acquired_at}")

        # Analyze video
        print("\n?? Analyzing video (audio + transcription)...")
        report = analyzer.analyze_video(
            video_path=str(smallest_file),
            case_number="25-41706",
            evidence_number=smallest_file.stem,
            acquired_by="Devon T. Barber",
            source="Discovery production",
        )

        # Display results
        print("\n" + "=" * 60)
        print("?? ANALYSIS RESULTS")
        print("=" * 60)

        print(f"\n?? File: {report.file_name}")
        print(f"?? Hash: {report.file_hash}")
        print(f"??  Duration: {report.duration:.1f} seconds")
        print(f"?? Analyzed: {report.analysis_date}")

        summary = report.generate_summary()

        print("\n?? Audio Transcription:")
        print(f"   Total speakers: {summary['total_speakers']}")
        print(f"   Total segments: {summary['total_segments']}")
        print(f"   Total words: {summary['total_words']}")

        if report.transcript:
            print("\n?? First 5 transcript segments:")
            for i, segment in enumerate(report.transcript[:5], 1):
                speaker = segment.speaker_label or segment.speaker or "Unknown"
                print(f"   {i}. [{segment.start_time:.1f}s] {speaker}: {segment.text[:80]}...")

        if report.speakers:
            print("\n?? Identified speakers:")
            for speaker_id, label in report.speakers.items():
                print(f"   - {speaker_id}: {label}")

        if report.entities:
            print("\n?? Entities found:")
            for entity_type, values in report.entities.items():
                print(f"   - {entity_type}: {len(values)} found")
                if values:
                    print(f"     Examples: {', '.join(values[:3])}")

        # Save report
        output_file = Path("bwc_analysis") / f"{smallest_file.stem}_analysis.json"
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

        print(f"\n?? Full report saved to: {output_file}")

        print("\n" + "=" * 60)
        print("? ANALYSIS COMPLETE!")
        print("=" * 60)

    except Exception as e:
        print(f"\n? Analysis failed: {e}")
        import traceback

        traceback.print_exc()

else:
    if not ANALYZER_AVAILABLE:
        print("\n??  ANALYSIS SKIPPED")
        print("   Install AI dependencies to run full analysis:")
        print("   > .\\scripts\\install-ai-FIXED.ps1")

# Check for PDFs
pdf_files = list(DISCOVERY_PATH.parent.glob("*.pdf"))
if pdf_files:
    print(f"\n?? PDF Documents found: {len(pdf_files)}")
    for pdf in pdf_files:
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"   - {pdf.name} ({size_mb:.1f} MB)")

print("\n" + "=" * 60)
print("?? DISCOVERY FILE SUMMARY")
print("=" * 60)
print(f"BWC Videos: {len(bwc_files)}")
print(f"Officers: {len(officers)}")
print(f"PDFs: {len(pdf_files)}")
print(f"Total BWC Size: {total_size:,.1f} MB ({total_size / 1024:.2f} GB)")
print("\n? Discovery files ready for analysis!")
print("=" * 60)
