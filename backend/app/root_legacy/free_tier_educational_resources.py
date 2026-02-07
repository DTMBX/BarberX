# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
FREE Tier Educational Resources
Guides, templates, and tutorials available to all users
Cost: $0 (static content)
"""

EDUCATIONAL_RESOURCES = {
    "guides": [
        {
            "id": "bwc_best_practices",
            "title": "Body-Worn Camera Best Practices",
            "category": "BWC Analysis",
            "description": "Learn how to effectively analyze body camera footage for legal review.",
            "duration": "10 min read",
            "icon": "video",
            "content_url": "/static/education/bwc_best_practices.html",
            "downloadable": True,
            "topics": [
                "Identifying critical timestamps",
                "Audio analysis techniques",
                "Fourth Amendment considerations",
                "Use of force timelines",
            ],
        },
        {
            "id": "pdf_evidence_review",
            "title": "PDF Evidence Review Guide",
            "category": "Document Analysis",
            "description": "Master the art of reviewing discovery documents and police reports.",
            "duration": "15 min read",
            "icon": "file-text",
            "content_url": "/static/education/pdf_evidence_guide.html",
            "downloadable": True,
            "topics": [
                "OCR quality optimization",
                "Keyword search strategies",
                "Cross-referencing documents",
                "Finding inconsistencies",
            ],
        },
        {
            "id": "case_law_search",
            "title": "Case Law Search Strategies",
            "category": "Legal Research",
            "description": "Effective techniques for finding relevant case law and precedents.",
            "duration": "12 min read",
            "icon": "search",
            "content_url": "/static/education/case_law_search.html",
            "downloadable": True,
            "topics": [
                "Boolean search operators",
                "Jurisdiction filtering",
                "Citation verification",
                "Updating case law",
            ],
        },
        {
            "id": "constitutional_issues",
            "title": "Spotting Constitutional Issues",
            "category": "Legal Analysis",
            "description": "Identify Fourth, Fifth, and Sixth Amendment violations in police conduct.",
            "duration": "20 min read",
            "icon": "shield",
            "content_url": "/static/education/constitutional_issues.html",
            "downloadable": True,
            "topics": [
                "Fourth Amendment searches",
                "Fifth Amendment Miranda",
                "Sixth Amendment counsel",
                "Qualified immunity",
            ],
        },
    ],
    "templates": [
        {
            "id": "motion_suppress_evidence",
            "title": "Motion to Suppress Evidence",
            "category": "Court Filings",
            "description": "Template for filing motions to suppress evidence based on constitutional violations.",
            "file_type": "DOCX",
            "file_size": "45 KB",
            "icon": "file",
            "download_url": "/static/templates/motion_suppress_evidence.docx",
            "preview_url": "/static/templates/previews/motion_suppress_evidence.jpg",
            "includes": [
                "Fourth Amendment violations",
                "Miranda violations",
                "Chain of custody issues",
                "Case law citations",
            ],
        },
        {
            "id": "use_of_force_analysis",
            "title": "Use of Force Analysis Report",
            "category": "Reports",
            "description": "Comprehensive template for analyzing use of force incidents.",
            "file_type": "DOCX",
            "file_size": "52 KB",
            "icon": "file",
            "download_url": "/static/templates/use_of_force_report.docx",
            "preview_url": "/static/templates/previews/use_of_force_report.jpg",
            "includes": [
                "Timeline reconstruction",
                "Graham v. Connor analysis",
                "Policy compliance review",
                "Expert opinion sections",
            ],
        },
        {
            "id": "discovery_request",
            "title": "Comprehensive Discovery Request",
            "category": "Discovery",
            "description": "Template for requesting all relevant evidence in criminal defense cases.",
            "file_type": "DOCX",
            "file_size": "38 KB",
            "icon": "file",
            "download_url": "/static/templates/discovery_request.docx",
            "preview_url": "/static/templates/previews/discovery_request.jpg",
            "includes": [
                "BWC footage requests",
                "CAD/RMS records",
                "Officer personnel files",
                "Dispatch recordings",
            ],
        },
        {
            "id": "bwc_timeline_worksheet",
            "title": "BWC Timeline Worksheet",
            "category": "Analysis Tools",
            "description": "Structured worksheet for creating detailed timelines from body camera footage.",
            "file_type": "XLSX",
            "file_size": "28 KB",
            "icon": "table",
            "download_url": "/static/templates/bwc_timeline_worksheet.xlsx",
            "preview_url": "/static/templates/previews/bwc_timeline.jpg",
            "includes": [
                "Timestamp tracking",
                "Event severity coding",
                "Officer statements log",
                "Auto-calculated durations",
            ],
        },
        {
            "id": "case_intake_form",
            "title": "Client Case Intake Form",
            "category": "Case Management",
            "description": "Initial client interview form for criminal defense cases.",
            "file_type": "PDF",
            "file_size": "120 KB",
            "icon": "clipboard",
            "download_url": "/static/templates/case_intake_form.pdf",
            "preview_url": "/static/templates/previews/case_intake.jpg",
            "includes": [
                "Client information",
                "Incident details",
                "Witness information",
                "Evidence checklist",
            ],
        },
    ],
    "video_tutorials": [
        {
            "id": "platform_overview",
            "title": "Evident Platform Overview",
            "category": "Getting Started",
            "description": "5-minute walkthrough of the Evident platform features.",
            "duration": "5:30",
            "thumbnail": "/static/videos/thumbnails/platform_overview.jpg",
            "video_url": "/static/videos/platform_overview.mp4",
            "transcript_available": True,
        },
        {
            "id": "uploading_bwc",
            "title": "Uploading & Analyzing BWC Footage",
            "category": "BWC Analysis",
            "description": "Step-by-step guide to uploading and analyzing body camera videos.",
            "duration": "7:15",
            "thumbnail": "/static/videos/thumbnails/uploading_bwc.jpg",
            "video_url": "/static/videos/uploading_bwc.mp4",
            "transcript_available": True,
        },
        {
            "id": "pdf_batch_upload",
            "title": "Batch PDF Upload & OCR",
            "category": "Document Analysis",
            "description": "Learn how to upload multiple PDFs and extract text with OCR.",
            "duration": "6:45",
            "thumbnail": "/static/videos/thumbnails/pdf_batch.jpg",
            "video_url": "/static/videos/pdf_batch_upload.mp4",
            "transcript_available": True,
        },
    ],
    "case_studies": [
        {
            "id": "successful_suppression",
            "title": "Case Study: Successful Evidence Suppression",
            "category": "Success Stories",
            "description": "How a public defender used Evident to identify Fourth Amendment violations.",
            "read_time": "8 min",
            "outcome": "Evidence Suppressed",
            "content_url": "/static/case-studies/successful_suppression.html",
        },
        {
            "id": "timeline_wins_trial",
            "title": "Case Study: Timeline Analysis Wins Trial",
            "category": "Success Stories",
            "description": "Defense attorney proves inconsistencies using BWC timeline analysis.",
            "read_time": "10 min",
            "outcome": "Not Guilty Verdict",
            "content_url": "/static/case-studies/timeline_wins_trial.html",
        },
    ],
}


def get_all_educational_resources():
    """Return all educational resources"""
    return EDUCATIONAL_RESOURCES


def get_resources_by_category(category):
    """Get educational resources filtered by category"""
    resources = {"guides": [], "templates": [], "video_tutorials": [], "case_studies": []}

    for resource_type, items in EDUCATIONAL_RESOURCES.items():
        for item in items:
            if item.get("category") == category:
                resources[resource_type].append(item)

    return resources


def get_resource_by_id(resource_id):
    """Get specific educational resource by ID"""
    for resource_type, items in EDUCATIONAL_RESOURCES.items():
        for item in items:
            if item.get("id") == resource_id:
                return item
    return None


def is_resource_available_for_tier(resource_id, tier):
    """
    Check if a resource is available for user's tier
    All educational resources are FREE for everyone
    """
    # All educational content is free
    return True


# Educational resource categories
CATEGORIES = [
    "Getting Started",
    "BWC Analysis",
    "Document Analysis",
    "Legal Research",
    "Legal Analysis",
    "Court Filings",
    "Discovery",
    "Reports",
    "Analysis Tools",
    "Case Management",
    "Success Stories",
]
