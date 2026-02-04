"""
FREE Tier Demo Cases
Pre-loaded sample cases with full reports for FREE tier users
Cost: $0 (pre-generated, no processing)
"""

from datetime import datetime, timedelta

from .models_auth import TierLevel

DEMO_CASES = [
    {
        "id": "demo_traffic_stop_2024",
        "title": "Traffic Stop - Use of Force Review",
        "case_number": "DEMO-2024-001",
        "incident_date": "2024-03-15",
        "officer_name": "Officer J. Smith (Demo)",
        "department": "Sample County Sheriff",
        "description": "Routine traffic stop escalating to use of force. Demonstrates BWC timeline analysis and Fourth Amendment review.",
        "case_type": "Use of Force",
        "status": "Closed - Educational Sample",
        "demo": True,
        "locked": True,  # Cannot edit demo cases
        # Pre-generated analysis
        "timeline": [
            {"time": "00:00", "event": "Traffic stop initiated", "severity": "low"},
            {"time": "01:23", "event": "Driver refuses license request", "severity": "medium"},
            {"time": "02:45", "event": "Verbal confrontation escalates", "severity": "medium"},
            {"time": "03:12", "event": "Officer orders driver out of vehicle", "severity": "high"},
            {"time": "03:58", "event": "Physical contact - officer grabs arm", "severity": "high"},
            {"time": "04:15", "event": "Driver placed in handcuffs", "severity": "high"},
            {"time": "05:30", "event": "Backup arrives", "severity": "low"},
        ],
        "transcription": """
[00:00] Officer Smith: Good afternoon. License and registration please.
[01:23] Driver: What did I do? Why are you pulling me over?
[01:28] Officer Smith: You failed to signal at the last intersection. License please.
[01:35] Driver: This is harassment. I'm not giving you anything.
[02:45] Officer Smith: Sir, I need you to comply with my lawful order.
[02:50] Driver: I know my rights. Am I being detained?
[03:12] Officer Smith: Step out of the vehicle now.
[03:58] Officer Smith: [Physical contact] Give me your hands.
[04:15] Officer Smith: You're under arrest for obstruction.
""",
        "ai_analysis": {
            "constitutional_issues": [
                "Fourth Amendment - Lawful Terry Stop (traffic violation observed)",
                "Pennsylvania v. Mimms - Officer may order driver from vehicle",
                "Obstruction charge appears justified based on refusal to comply",
            ],
            "policy_compliance": "Officer followed department escalation policy. Verbal commands given before physical contact.",
            "recommendations": "Body camera footage supports officer's account. No policy violations identified.",
            "risk_level": "Low",
            "case_law_citations": [
                "Terry v. Ohio, 392 U.S. 1 (1968)",
                "Pennsylvania v. Mimms, 434 U.S. 106 (1977)",
                "Whren v. United States, 517 U.S. 806 (1996)",
            ],
        },
        "files": [
            {
                "name": "traffic_stop_bwc.mp4",
                "type": "video",
                "duration": "5:30",
                "size_mb": 45,
                "demo_url": "/static/demos/traffic_stop_preview.jpg",  # Thumbnail only
            }
        ],
    },
    {
        "id": "demo_wellness_check_2024",
        "title": "Wellness Check - Mental Health Crisis",
        "case_number": "DEMO-2024-002",
        "incident_date": "2024-05-22",
        "officer_name": "Officer M. Rodriguez (Demo)",
        "department": "Sample City Police",
        "description": "Mental health crisis call demonstrating de-escalation techniques and crisis intervention.",
        "case_type": "Wellness Check",
        "status": "Closed - Educational Sample",
        "demo": True,
        "locked": True,
        "timeline": [
            {
                "time": "00:00",
                "event": "Dispatch - welfare check requested by family",
                "severity": "low",
            },
            {"time": "02:15", "event": "Contact with subject at residence", "severity": "medium"},
            {"time": "03:40", "event": "Subject expressing suicidal ideation", "severity": "high"},
            {"time": "05:20", "event": "CIT officer employs de-escalation", "severity": "high"},
            {
                "time": "08:15",
                "event": "Subject agrees to voluntary evaluation",
                "severity": "medium",
            },
            {"time": "10:00", "event": "EMS transports to hospital", "severity": "low"},
        ],
        "transcription": """
[00:00] Dispatcher: Unit 12, welfare check at 456 Oak Street. Family concerned.
[02:15] Officer Rodriguez: Hello, my name is Officer Rodriguez. Your family asked us to check on you.
[03:40] Subject: I don't want to be here anymore. Nothing matters.
[05:20] Officer Rodriguez: I understand you're going through a difficult time. Let's talk about getting you some help.
[08:15] Subject: Okay... I think I need to talk to someone.
[10:00] Officer Rodriguez: EMS is here. They're going to take good care of you.
""",
        "ai_analysis": {
            "constitutional_issues": [
                "Community caretaking exception - wellness check justified",
                "Voluntary vs. involuntary commitment - subject agreed voluntarily",
                "Mental health hold criteria not required in this case",
            ],
            "policy_compliance": "Excellent use of CIT training. Officer de-escalated effectively without use of force.",
            "recommendations": "Exemplary response. Recommend for training purposes. Officer showed patience and empathy.",
            "risk_level": "Low (Handled Appropriately)",
            "case_law_citations": [
                "Cady v. Dombrowski, 413 U.S. 433 (1973) - Community caretaking",
                "Local mental health hold statutes",
            ],
        },
        "files": [
            {
                "name": "wellness_check_bwc.mp4",
                "type": "video",
                "duration": "10:00",
                "size_mb": 82,
                "demo_url": "/static/demos/wellness_check_preview.jpg",
            }
        ],
    },
    {
        "id": "demo_search_warrant_2024",
        "title": "Search Warrant Execution - Evidence Review",
        "case_number": "DEMO-2024-003",
        "incident_date": "2024-07-10",
        "officer_name": "Detective L. Johnson (Demo)",
        "department": "Sample County DA's Office",
        "description": "Search warrant execution with PDF evidence review demonstrating document analysis and chain of custody.",
        "case_type": "Search Warrant",
        "status": "Closed - Educational Sample",
        "demo": True,
        "locked": True,
        "timeline": [
            {"time": "06:00", "event": "Search warrant approved by judge", "severity": "low"},
            {"time": "07:30", "event": "Team briefing at station", "severity": "low"},
            {"time": "08:15", "event": "Arrival at target location", "severity": "medium"},
            {"time": "08:20", "event": "Entry and announcement", "severity": "high"},
            {"time": "08:45", "event": "Evidence located - documents seized", "severity": "medium"},
            {"time": "10:00", "event": "Scene secured, evidence logged", "severity": "low"},
        ],
        "ai_analysis": {
            "constitutional_issues": [
                "Fourth Amendment - Valid search warrant with probable cause",
                "Knock and announce rule - Complied",
                "Scope of search - Within parameters of warrant",
                "Chain of custody - Properly documented",
            ],
            "policy_compliance": "All department search warrant protocols followed. Evidence properly documented and secured.",
            "recommendations": "No issues identified. Warrant execution was textbook. Evidence admissible.",
            "risk_level": "Low",
            "case_law_citations": [
                "Illinois v. Gates, 462 U.S. 213 (1983) - Probable cause",
                "Wilson v. Arkansas, 514 U.S. 927 (1995) - Knock and announce",
                "Maryland v. Garrison, 480 U.S. 79 (1987) - Scope of warrant",
            ],
        },
        "documents": [
            {
                "name": "search_warrant_affidavit.pdf",
                "type": "pdf",
                "pages": 8,
                "size_mb": 2.3,
                "summary": "Affidavit establishing probable cause for search of residence. Details confidential informant information and corroborating surveillance.",
                "demo_url": "/static/demos/warrant_affidavit_preview.jpg",
            },
            {
                "name": "evidence_log.pdf",
                "type": "pdf",
                "pages": 3,
                "size_mb": 0.8,
                "summary": "Chain of custody documentation for all items seized. Includes photos and officer signatures.",
                "demo_url": "/static/demos/evidence_log_preview.jpg",
            },
        ],
    },
]


def get_demo_cases():
    """Return all demo cases"""
    return DEMO_CASES


def get_demo_case_by_id(case_id):
    """Get specific demo case by ID"""
    for case in DEMO_CASES:
        if case["id"] == case_id:
            return case
    return None


def assign_demo_cases_to_user(user):
    """
    Assign demo cases to a FREE tier user
    These are virtual cases - no database storage needed
    Returns list of demo case IDs
    """
    if user.tier == TierLevel.FREE:
        return [case["id"] for case in DEMO_CASES]
    return []


def is_demo_case(case_id):
    """Check if a case ID is a demo case"""
    return case_id.startswith("demo_")


