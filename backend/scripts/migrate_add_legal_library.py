# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database migration for Legal Reference Library

Creates tables for:
- legal_documents
- citations
- document_annotations
- legal_topics
"""

import sys

from legal_library import LegalTopic
from models_auth import db


def create_legal_library_tables():
    """Create all legal library tables"""

    print("Creating Legal Reference Library tables...")

    try:
        # Create tables
        db.create_all()

        # Add some initial legal topics
        initial_topics = [
            (
                "Constitutional Law",
                "Issues related to constitutional interpretation and application",
            ),
            ("4th Amendment", "Search and seizure, warrants, probable cause"),
            ("5th Amendment", "Self-incrimination, Miranda rights, due process"),
            ("6th Amendment", "Right to counsel, speedy trial, confrontation"),
            ("14th Amendment", "Due process, equal protection"),
            ("Civil Rights", "Section 1983 claims, constitutional violations"),
            ("Excessive Force", "Police use of force, qualified immunity"),
            ("Criminal Procedure", "Pretrial, trial, and post-trial procedures"),
            ("Evidence", "Admissibility, hearsay, authentication"),
            ("Employment Law", "Discrimination, wrongful termination, labor"),
        ]

        for name, description in initial_topics:
            # Check if exists
            if not LegalTopic.query.filter_by(name=name).first():
                topic = LegalTopic(name=name, description=description)
                db.session.add(topic)

        db.session.commit()

        print("✅ Legal library tables created successfully!")
        print("   - legal_documents")
        print("   - citations")
        print("   - document_annotations")
        print("   - legal_topics")
        print(f"   - {len(initial_topics)} initial topics added")

        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        db.session.rollback()
        return False


if __name__ == "__main__":
    # Run migration
    from app import app

    with app.app_context():
        success = create_legal_library_tables()
        sys.exit(0 if success else 1)
