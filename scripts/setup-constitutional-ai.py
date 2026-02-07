# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Constitutional AI Setup
Configures AI models for constitutional violation detection
License: Proprietary (Evident Legal Technologies)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Constitutional violation patterns and case law database
CONSTITUTIONAL_VIOLATIONS = {
    "miranda_violations": {
        "patterns": [
            "did not read miranda rights",
            "failed to inform of right to remain silent",
            "questioned without attorney present",
            "continued interrogation after requesting lawyer",
            "coerced confession",
        ],
        "amendments": ["5th Amendment", "6th Amendment"],
        "key_cases": [
            "Miranda v. Arizona, 384 U.S. 436 (1966)",
            "Edwards v. Arizona, 451 U.S. 477 (1981)",
            "Davis v. United States, 512 U.S. 452 (1994)",
        ],
        "damages_range": [50000, 500000],
    },
    "fourth_amendment_violations": {
        "patterns": [
            "warrantless search",
            "illegal stop and frisk",
            "search without probable cause",
            "unreasonable seizure",
            "unlawful detention",
            "pretextual traffic stop",
            "excessive force during arrest",
        ],
        "amendments": ["4th Amendment"],
        "key_cases": [
            "Terry v. Ohio, 392 U.S. 1 (1968)",
            "Illinois v. Wardlow, 528 U.S. 119 (2000)",
            "Rodriguez v. United States, 575 U.S. 348 (2015)",
            "Utah v. Strieff, 579 U.S. 232 (2016)",
        ],
        "damages_range": [25000, 250000],
    },
    "excessive_force": {
        "patterns": [
            "excessive force",
            "unreasonable force",
            "choke hold",
            "taser deployment without justification",
            "beating while handcuffed",
            "k9 attack without warning",
            "shot unarmed suspect",
        ],
        "amendments": ["4th Amendment", "8th Amendment"],
        "key_cases": [
            "Graham v. Connor, 490 U.S. 386 (1989)",
            "Tennessee v. Garner, 471 U.S. 1 (1985)",
            "Kingsley v. Hendrickson, 576 U.S. 389 (2015)",
        ],
        "damages_range": [100000, 5000000],
    },
    "first_amendment_violations": {
        "patterns": [
            "arrested for filming police",
            "retaliation for speech",
            "prevented from recording",
            "seized camera or phone",
            "arrested for protesting",
        ],
        "amendments": ["1st Amendment"],
        "key_cases": [
            "Glik v. Cunniffe, 655 F.3d 78 (1st Cir. 2011)",
            "Turner v. Driver, 848 F.3d 678 (5th Cir. 2017)",
            "Fields v. City of Philadelphia, 862 F.3d 353 (3rd Cir. 2017)",
        ],
        "damages_range": [25000, 250000],
    },
    "false_arrest": {
        "patterns": [
            "arrested without probable cause",
            "false arrest",
            "wrongful detention",
            "arrest on fabricated charges",
            "arrest in retaliation",
        ],
        "amendments": ["4th Amendment"],
        "key_cases": [
            "Dunaway v. New York, 442 U.S. 200 (1979)",
            "Michigan v. DeFillippo, 443 U.S. 31 (1979)",
        ],
        "damages_range": [50000, 500000],
    },
    "malicious_prosecution": {
        "patterns": [
            "charges filed without evidence",
            "prosecution after exoneration",
            "knowingly false testimony",
            "withheld exculpatory evidence",
        ],
        "amendments": ["4th Amendment", "14th Amendment"],
        "key_cases": [
            "Albright v. Oliver, 510 U.S. 266 (1994)",
            "Thompson v. Clark, 596 U.S. ___ (2022)",
        ],
        "damages_range": [100000, 1000000],
    },
    "brady_violations": {
        "patterns": [
            "withheld exculpatory evidence",
            "suppressed favorable evidence",
            "failed to disclose impeachment evidence",
        ],
        "amendments": ["14th Amendment - Due Process"],
        "key_cases": [
            "Brady v. Maryland, 373 U.S. 83 (1963)",
            "Giglio v. United States, 405 U.S. 150 (1972)",
            "Kyles v. Whitley, 514 U.S. 419 (1995)",
        ],
        "damages_range": [250000, 2000000],
    },
    "qualified_immunity_exceptions": {
        "clearly_established_law": [
            "Right to be free from excessive force was clearly established",
            "Right to record police was clearly established in this circuit",
            "Miranda requirements were clearly established",
            "Warrantless search violations were clearly established",
        ],
        "cases": ["Hope v. Pelzer, 536 U.S. 730 (2002)", "Taylor v. Riojas, 592 U.S. ___ (2020)"],
    },
}


def setup_constitutional_ai():
    """Initialize AI models and constitutional violation database"""

    print("?? Setting up Constitutional AI Analysis System...")
    print("=" * 60)

    # Check for API keys
    print("\n[1/5] Checking API keys...")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if openai_key:
        print("  ? OpenAI API key found")
    else:
        print("  ??  OpenAI API key not found (optional but recommended)")

    if anthropic_key:
        print("  ? Anthropic API key found")
    else:
        print("  ??  Anthropic API key not found (optional)")

    # Setup vector database for case law
    print("\n[2/5] Setting up case law vector database...")
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        client = chromadb.Client()

        # Create collection for constitutional case law
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        collection = client.create_collection(
            name="constitutional_case_law",
            embedding_function=sentence_transformer_ef,
            metadata={
                "description": "Supreme Court and Circuit Court cases on constitutional rights"
            },
        )

        # Add constitutional violations to vector DB
        case_docs = []
        case_metadata = []
        case_ids = []

        for violation_type, data in CONSTITUTIONAL_VIOLATIONS.items():
            for i, case in enumerate(data.get("key_cases", [])):
                case_docs.append(f"{violation_type}: {case}")
                case_metadata.append(
                    {
                        "violation_type": violation_type,
                        "case": case,
                        "amendments": ", ".join(data.get("amendments", [])),
                        "min_damages": data.get("damages_range", [0, 0])[0],
                        "max_damages": data.get("damages_range", [0, 0])[1],
                    }
                )
                case_ids.append(f"{violation_type}_{i}")

        collection.add(documents=case_docs, metadatas=case_metadata, ids=case_ids)

        print(f"  ? Vector database created with {len(case_docs)} cases")

    except Exception as e:
        print(f"  ??  Vector database setup failed: {e}")

    # Download Whisper model
    print("\n[3/5] Downloading Whisper AI model...")
    try:
        import whisper

        model = whisper.load_model("base")
        print("  ? Whisper model downloaded (base)")
    except Exception as e:
        print(f"  ??  Whisper download failed: {e}")

    # Download SpaCy legal model
    print("\n[4/5] Verifying SpaCy legal NLP...")
    try:
        import spacy

        nlp = spacy.load("en_core_web_lg")
        print("  ? SpaCy legal model ready")
    except Exception as e:
        print(f"  ??  SpaCy model not found: {e}")

    # Create constitutional violation detector
    print("\n[5/5] Creating constitutional violation detector...")

    detector_code = (
        '''"""
Constitutional Violation Detector
Auto-generated AI model for detecting constitutional violations
"""

from typing import Dict, List, Optional
import re

class ConstitutionalViolationDetector:
    """Detect constitutional violations in legal documents and transcripts"""
    
    def __init__(self):
        self.violations_db = VIOLATIONS_DB
    
    def analyze_text(self, text: str) -> List[Dict]:
        """Analyze text for constitutional violations"""
        violations = []
        text_lower = text.lower()
        
        for violation_type, data in self.violations_db.items():
            for pattern in data["patterns"]:
                if pattern.lower() in text_lower:
                    violations.append({
                        "type": violation_type,
                        "description": pattern,
                        "amendments": data["amendments"],
                        "key_cases": data["key_cases"],
                        "damages_range": data["damages_range"],
                        "severity": self._calculate_severity(violation_type)
                    })
        
        return violations
    
    def _calculate_severity(self, violation_type: str) -> str:
        """Calculate severity level"""
        high_severity = ["excessive_force", "malicious_prosecution", "brady_violations"]
        if violation_type in high_severity:
            return "High"
        return "Medium"

VIOLATIONS_DB = '''
        + str(CONSTITUTIONAL_VIOLATIONS)
        + """
"""
    )

    # Write detector to file
    with open("constitutional_violation_detector.py", "w", encoding="utf-8") as f:
        f.write(detector_code)

    print("  ? Constitutional violation detector created")

    print("\n" + "=" * 60)
    print("? Constitutional AI Setup Complete!")
    print("=" * 60)

    print("\n?? Ready to detect:")
    print("  � Miranda violations")
    print("  � 4th Amendment violations")
    print("  � Excessive force")
    print("  � False arrest")
    print("  � Malicious prosecution")
    print("  � Brady violations")
    print("  � 1st Amendment retaliation")

    print("\n?? Loaded case law:")
    print(
        f"  � {len([c for v in CONSTITUTIONAL_VIOLATIONS.values() for c in v.get('key_cases', [])])} Supreme Court & Circuit cases"
    )

    print("\n?? Next steps:")
    print("  1. Upload BWC video to /upload")
    print("  2. System will auto-detect constitutional violations")
    print("  3. Review violations at /auth/dashboard")
    print("")


if __name__ == "__main__":
    setup_constitutional_ai()
