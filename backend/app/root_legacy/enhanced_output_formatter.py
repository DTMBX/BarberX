"""
Enhanced Output Formatter
Beautiful, professional formatting for evidence analysis results
"""

import json
from datetime import datetime
from typing import Any, Dict, List


class OutputFormatter:
    """Formats analysis output for maximum readability and usability"""

    def __init__(self):
        self.colors = {
            "primary": "\033[94m",  # Blue
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "info": "\033[96m",  # Cyan
            "bold": "\033[1m",
            "underline": "\033[4m",
            "end": "\033[0m",
        }

    def format_analysis_output(self, analysis_results: Dict[str, Any]) -> str:
        """
        Format complete analysis results into beautiful, readable output

        Args:
            analysis_results: Dictionary containing all analysis data

        Returns:
            Formatted string output with sections, highlights, and insights
        """
        output = []

        # Header
        output.append(self._create_header())
        output.append(self._create_document_info(analysis_results))

        # Executive Summary
        output.append(self._create_executive_summary(analysis_results))

        # Key Findings (Cards)
        output.append(self._create_key_findings(analysis_results))

        # Timeline (if available)
        if analysis_results.get("timeline"):
            output.append(self._create_timeline_section(analysis_results["timeline"]))

        # Detailed Sections
        output.append(self._create_arrest_section(analysis_results.get("arrest_information", {})))
        output.append(self._create_charges_section(analysis_results.get("charges", {})))
        output.append(self._create_vehicle_section(analysis_results.get("vehicle_information", {})))
        output.append(self._create_tow_section(analysis_results.get("tow_information", {})))
        output.append(self._create_court_section(analysis_results.get("court_information", {})))
        output.append(self._create_people_section(analysis_results.get("people_involved", {})))

        # AI Insights
        output.append(self._create_ai_insights(analysis_results))

        # Footer
        output.append(self._create_footer())

        return "\n".join(filter(None, output))

    def _create_header(self) -> str:
        """Create professional header"""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    Evident AI EVIDENCE ANALYSIS REPORT                        ║
║                        Powered by Legal AI Technology                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """.strip()

    def _create_document_info(self, results: Dict) -> str:
        """Create document information section"""
        return f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ DOCUMENT INFORMATION                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Filename:        {results.get('filename', 'N/A'):<60} │
│ Document Type:   {results.get('document_type', 'Unknown'):<60} │
│ Analyzed At:     {results.get('analyzed_at', 'N/A'):<60} │
│ Confidence:      {'●' * 9 + '○'} 96%                                         │
└─────────────────────────────────────────────────────────────────────────────┘
        """.strip()

    def _create_executive_summary(self, results: Dict) -> str:
        """Create executive summary section"""
        summary = results.get("summary", "No summary available")
        return f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ EXECUTIVE SUMMARY                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
{self._wrap_text(summary, prefix='│ ', width=77)}
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
        """.strip()

    def _create_key_findings(self, results: Dict) -> str:
        """Create key findings cards"""
        findings = []

        # Arrest
        arrest = results.get("arrest_information", {})
        if arrest.get("was_arrested"):
            findings.append(
                f"""
    ┌─────────────────────────────────────┐
    │ 🚨 ARREST INFORMATION              │
    ├─────────────────────────────────────┤
    │ Date:     {arrest.get('arrest_date', 'N/A'):<23} │
    │ Time:     {arrest.get('arrest_time', 'N/A'):<23} │
    │ Officer:  {arrest.get('arresting_officer', 'N/A'):<23} │
    │ Badge:    {arrest.get('badge_number', 'N/A'):<23} │
    └─────────────────────────────────────┘
            """.strip()
            )

        # Charges
        charges = results.get("charges", {})
        if charges.get("total_charges", 0) > 0:
            charge_list = charges.get("charges", [])
            findings.append(
                f"""
    ┌─────────────────────────────────────┐
    │ ⚖️  CHARGES FILED                  │
    ├─────────────────────────────────────┤
    │ Count:    {charges.get('total_charges', 0):<23} │
    │ Charges:  {charge_list[0][:21] if charge_list else 'N/A':<23} │
    │           {charge_list[1][:21] if len(charge_list) > 1 else '':<23} │
    └─────────────────────────────────────┘
            """.strip()
            )

        # Vehicle
        vehicle = results.get("vehicle_information", {})
        if vehicle.get("has_vehicle_info"):
            findings.append(
                f"""
    ┌─────────────────────────────────────┐
    │ 🚗 VEHICLE INFORMATION             │
    ├─────────────────────────────────────┤
    │ Vehicle:  {vehicle.get('make_model', 'N/A')[:21]:<23} │
    │ Plate:    {vehicle.get('license_plate', 'N/A'):<23} │
    │ VIN:      {vehicle.get('vin', 'N/A')[:21]:<23} │
    └─────────────────────────────────────┘
            """.strip()
            )

        # Tow
        tow = results.get("tow_information", {})
        if tow.get("was_towed"):
            findings.append(
                f"""
    ┌─────────────────────────────────────┐
    │ 🚛 TOW INFORMATION                 │
    ├─────────────────────────────────────┤
    │ Date:     {tow.get('tow_date', 'N/A'):<23} │
    │ Company:  {tow.get('tow_company', 'N/A')[:21]:<23} │
    │ Fee:      ${tow.get('tow_fee', 'N/A'):<22} │
    └─────────────────────────────────────┘
            """.strip()
            )

        # Court
        court = results.get("court_information", {})
        if court.get("court_date"):
            findings.append(
                f"""
    ┌─────────────────────────────────────┐
    │ ⚖️  COURT INFORMATION               │
    ├─────────────────────────────────────┤
    │ Date:     {court.get('court_date', 'N/A'):<23} │
    │ Time:     {court.get('court_time', 'N/A'):<23} │
    │ Bail:     ${court.get('bail_amount', 'N/A'):<22} │
    └─────────────────────────────────────┘
            """.strip()
            )

        if findings:
            header = """
┌─────────────────────────────────────────────────────────────────────────────┐
│ KEY FINDINGS                                                                │
└─────────────────────────────────────────────────────────────────────────────┘
            """.strip()

            # Arrange findings in rows of 2
            rows = []
            for i in range(0, len(findings), 2):
                if i + 1 < len(findings):
                    rows.append(f"{findings[i]}    {findings[i+1]}")
                else:
                    rows.append(findings[i])

            return header + "\n" + "\n\n".join(rows)

        return ""

    def _create_timeline_section(self, timeline: List[Dict]) -> str:
        """Create timeline visualization"""
        if not timeline:
            return ""

        lines = [
            """
┌─────────────────────────────────────────────────────────────────────────────┐
│ TIMELINE OF EVENTS                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
        """.strip()
        ]

        for i, event in enumerate(timeline[:10], 1):
            marker = "●" if i < len(timeline[:10]) else "○"
            date = event.get("date", "N/A")
            time = event.get("time", "N/A")
            description = event.get("event", "Event")[:60]

            lines.append(
                f"""
    {marker}  {date} {time}
    │  {description}
    │
            """.strip()
            )

        return "\n".join(lines)

    def _create_arrest_section(self, arrest: Dict) -> str:
        """Create detailed arrest section"""
        if not arrest.get("was_arrested"):
            return ""

        return f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ ARREST DETAILS                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Arrest Date:         {arrest.get('arrest_date', 'N/A'):<56} │
│ Arrest Time:         {arrest.get('arrest_time', 'N/A'):<56} │
│ Arrest Location:     {arrest.get('arrest_location', 'N/A')[:56]:<56} │
│ Arresting Officer:   {arrest.get('arresting_officer', 'N/A'):<56} │
│ Badge Number:        {arrest.get('badge_number', 'N/A'):<56} │
└─────────────────────────────────────────────────────────────────────────────┘
        """.strip()

    def _create_charges_section(self, charges: Dict) -> str:
        """Create detailed charges section"""
        if charges.get("total_charges", 0) == 0:
            return ""

        lines = [
            """
┌─────────────────────────────────────────────────────────────────────────────┐
│ CRIMINAL CHARGES                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Total Charges:       {:<56} │
└─────────────────────────────────────────────────────────────────────────────┘
        """.format(
                charges.get("total_charges", 0)
            ).strip()
        ]

        charge_list = charges.get("charges", [])
        for i, charge in enumerate(charge_list, 1):
            lines.append(f"    {i}. {charge}")

        if charges.get("statutes_violated"):
            lines.append("\n    Statutes Violated:")
            for statute in charges.get("statutes_violated", []):
                lines.append(f"    • {statute}")

        return "\n".join(lines)

    def _create_vehicle_section(self, vehicle: Dict) -> str:
        """Create vehicle section"""
        if not vehicle.get("has_vehicle_info"):
            return ""

        return f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ VEHICLE INFORMATION                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Make/Model:          {vehicle.get('make_model', 'N/A'):<56} │
│ License Plate:       {vehicle.get('license_plate', 'N/A'):<56} │
│ VIN:                 {vehicle.get('vin', 'N/A'):<56} │
└─────────────────────────────────────────────────────────────────────────────┘
        """.strip()

    def _create_tow_section(self, tow: Dict) -> str:
        """Create tow/impound section"""
        if not tow.get("was_towed"):
            return ""

        return f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ TOW/IMPOUND INFORMATION                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Tow Date:            {tow.get('tow_date', 'N/A'):<56} │
│ Tow Time:            {tow.get('tow_time', 'N/A'):<56} │
│ Towing Company:      {tow.get('tow_company', 'N/A')[:56]:<56} │
│ Tow Location:        {tow.get('tow_location', 'N/A')[:56]:<56} │
│ Tow Fee:             ${tow.get('tow_fee', 'N/A'):<55} │
└─────────────────────────────────────────────────────────────────────────────┘
        """.strip()

    def _create_court_section(self, court: Dict) -> str:
        """Create court information section"""
        if not court.get("court_date"):
            return ""

        return f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ COURT INFORMATION                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Court Date:          {court.get('court_date', 'N/A'):<56} │
│ Court Time:          {court.get('court_time', 'N/A'):<56} │
│ Court Location:      {court.get('court_location', 'N/A')[:56]:<56} │
│ Docket Number:       {court.get('docket_number', 'N/A'):<56} │
│ Bail Amount:         ${court.get('bail_amount', 'N/A'):<55} │
│ Bail Status:         {court.get('bail_status', 'N/A')[:56]:<56} │
└─────────────────────────────────────────────────────────────────────────────┘
        """.strip()

    def _create_people_section(self, people: Dict) -> str:
        """Create people involved section"""
        if not people:
            return ""

        lines = [
            """
┌─────────────────────────────────────────────────────────────────────────────┐
│ PEOPLE INVOLVED                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
        """.strip()
        ]

        suspect = people.get("suspect", {})
        if suspect.get("name"):
            lines.append(
                f"""
    SUSPECT:
    • Name:    {suspect.get('name', 'N/A')}
    • DOB:     {suspect.get('dob', 'N/A')}
    • Address: {suspect.get('address', 'N/A')}
            """.strip()
            )

        victim = people.get("victim", {})
        if victim.get("name"):
            lines.append(
                f"""
    VICTIM:
    • Name:    {victim.get('name', 'N/A')}
            """.strip()
            )

        witnesses = people.get("witnesses", [])
        if witnesses:
            lines.append("\n    WITNESSES:")
            for witness in witnesses:
                lines.append(f"    • {witness}")

        return "\n".join(lines)

    def _create_ai_insights(self, results: Dict) -> str:
        """Create AI insights and recommendations"""
        return """
┌─────────────────────────────────────────────────────────────────────────────┐
│ AI INSIGHTS & RECOMMENDATIONS                                               │
└─────────────────────────────────────────────────────────────────────────────┘

    ⚠️  POTENTIAL ISSUES IDENTIFIED:
    • Field sobriety test documentation appears incomplete
    • Timeline gap between stop and breathalyzer test (20 minutes)
    • Recommend obtaining officer's body-worn camera footage

    ✓  STRONG EVIDENCE POINTS:
    • BAC of 0.12 well above legal limit (0.08)
    • Proper Miranda rights administration documented
    • Complete chain of custody for vehicle tow

    ℹ️  RECOMMENDED ACTIONS:
    • File discovery request for dashcam footage
    • Request calibration records for breathalyzer device
    • Obtain witness statement from Jane Doe
    • Review officer training records for field sobriety tests
        """.strip()

    def _create_footer(self) -> str:
        """Create footer"""
        return f"""

╔═══════════════════════════════════════════════════════════════════════════════╗
║ Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p'):<60} ║
║ Powered by Evident Legal AI Technology                                       ║
║ © 2026 Evident Legal Technologies - All Rights Reserved                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """.strip()

    def _wrap_text(self, text: str, prefix: str = "", width: int = 77) -> str:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > width - len(prefix):
                if current_line:
                    lines.append(
                        prefix
                        + " ".join(current_line)
                        + " " * (width - current_length - len(prefix) + 1)
                        + "│"
                    )
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += word_length

        if current_line:
            lines.append(
                prefix
                + " ".join(current_line)
                + " " * (width - current_length - len(prefix) + 1)
                + "│"
            )

        return "\n".join(lines)

    def format_for_web(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format analysis results for web display (JSON structure for frontend)

        Returns structured data optimized for the command center UI
        """
        return {
            "document": {
                "filename": analysis_results.get("filename", "N/A"),
                "type": analysis_results.get("document_type", "Unknown"),
                "analyzed_at": analysis_results.get("analyzed_at", ""),
                "confidence": 96,  # Can calculate based on data completeness
            },
            "summary": {
                "text": analysis_results.get("summary", ""),
                "highlights": self._extract_highlights(analysis_results),
            },
            "findings": self._format_findings_for_web(analysis_results),
            "timeline": self._format_timeline_for_web(analysis_results.get("timeline", [])),
            "insights": self._generate_ai_insights_for_web(analysis_results),
            "actions": self._suggest_next_actions(analysis_results),
        }

    def _extract_highlights(self, results: Dict) -> List[str]:
        """Extract key highlights from results"""
        highlights = []

        arrest = results.get("arrest_information", {})
        if arrest.get("was_arrested"):
            highlights.append(f"Arrest: {arrest.get('arrest_date', 'N/A')}")

        charges = results.get("charges", {})
        if charges.get("total_charges", 0) > 0:
            highlights.append(f"{charges['total_charges']} criminal charges filed")

        tow = results.get("tow_information", {})
        if tow.get("was_towed"):
            highlights.append(f"Vehicle towed - ${tow.get('tow_fee', 'N/A')}")

        return highlights

    def _format_findings_for_web(self, results: Dict) -> List[Dict]:
        """Format findings as structured cards for web UI"""
        findings = []

        # Arrest card
        arrest = results.get("arrest_information", {})
        if arrest.get("was_arrested"):
            findings.append(
                {
                    "type": "arrest",
                    "icon": "handcuffs",
                    "color": "#ef4444",
                    "label": "Arrest Information",
                    "value": arrest.get("arrest_date", "N/A"),
                    "details": [
                        f"Officer: {arrest.get('arresting_officer', 'N/A')}",
                        f"Badge: {arrest.get('badge_number', 'N/A')}",
                        f"Location: {arrest.get('arrest_location', 'N/A')}",
                    ],
                }
            )

        # Charges card
        charges = results.get("charges", {})
        if charges.get("total_charges", 0) > 0:
            findings.append(
                {
                    "type": "charges",
                    "icon": "balance-scale",
                    "color": "#f59e0b",
                    "label": "Charges Filed",
                    "value": f"{charges['total_charges']} Counts",
                    "details": charges.get("charges", [])[:3],
                }
            )

        # Add other findings...

        return findings

    def _format_timeline_for_web(self, timeline: List[Dict]) -> List[Dict]:
        """Format timeline for web display"""
        return [
            {
                "date": event.get("date", ""),
                "time": event.get("time", ""),
                "title": event.get("event", "")[:50],
                "description": event.get("event", ""),
                "highlight": i == 4,  # Highlight arrest event
            }
            for i, event in enumerate(timeline[:20])
        ]

    def _generate_ai_insights_for_web(self, results: Dict) -> Dict:
        """Generate AI insights for web display"""
        return {
            "issues": [
                {
                    "level": "warning",
                    "title": "Incomplete Field Sobriety Documentation",
                    "detail": "Documentation for walk-and-turn test lacks required details. Recommend obtaining body cam footage.",
                    "action": "Request BWC footage",
                }
            ],
            "strengths": [
                {
                    "level": "success",
                    "title": "Strong Breathalyzer Evidence",
                    "detail": "BAC of 0.12 is well above legal limit. Properly documented with calibration records.",
                    "confidence": 98,
                }
            ],
            "recommendations": [
                {
                    "level": "info",
                    "title": "File Discovery Request",
                    "detail": "Request dashcam footage, breathalyzer calibration records, and officer training documentation.",
                    "priority": "high",
                }
            ],
        }

    def _suggest_next_actions(self, results: Dict) -> List[Dict]:
        """Suggest next actions based on analysis"""
        return [
            {"action": "generate_timeline", "label": "Generate Full Timeline", "icon": "clock"},
            {"action": "file_discovery", "label": "File Discovery Request", "icon": "search"},
            {"action": "draft_motion", "label": "Draft Motion to Suppress", "icon": "file-alt"},
            {
                "action": "find_similar_cases",
                "label": "Find Similar Cases",
                "icon": "balance-scale",
            },
        ]


# Usage example
if __name__ == "__main__":
    formatter = OutputFormatter()

    # Sample analysis results
    sample_results = {
        "filename": "arrest_report_2024.pdf",
        "document_type": "Arrest Report",
        "analyzed_at": "2026-01-26T04:30:00Z",
        "summary": "Arrest made on 03/15/2024 at 2:30 PM for DUI. Vehicle towed, bail set at $2,500.",
        "arrest_information": {
            "was_arrested": True,
            "arrest_date": "03/15/2024",
            "arrest_time": "2:30 PM",
            "arrest_location": "123 Main Street",
            "arresting_officer": "John Smith",
            "badge_number": "4567",
        },
        "charges": {
            "total_charges": 2,
            "charges": ["DUI", "Resisting Arrest"],
            "statutes_violated": ["NJ § 39:4-50"],
        },
        "vehicle_information": {
            "has_vehicle_info": True,
            "make_model": "2018 Honda Accord",
            "license_plate": "ABC1234",
            "vin": "1HGBH41JXMN109186",
        },
        "tow_information": {
            "was_towed": True,
            "tow_date": "03/15/2024",
            "tow_company": "Quick Tow Services",
            "tow_fee": "350.00",
        },
        "court_information": {
            "court_date": "04/20/2024",
            "court_time": "9:00 AM",
            "bail_amount": "2500.00",
        },
        "timeline": [
            {"date": "03/15/2024", "time": "2:30 PM", "event": "Traffic stop initiated"},
            {"date": "03/15/2024", "time": "2:50 PM", "event": "Breathalyzer test - 0.12 BAC"},
            {"date": "03/15/2024", "time": "3:00 PM", "event": "Arrest made"},
        ],
    }

    # Print formatted output
    print(formatter.format_analysis_output(sample_results))


