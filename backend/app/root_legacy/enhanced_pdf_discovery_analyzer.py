"""
Enhanced PDF Discovery Analyzer
Extracts specific legal information: arrest details, tow records, citations, charges, timeline, etc.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class PDFDiscoveryAnalyzer:
    """Analyzes PDF discovery documents for specific legal information"""

    def __init__(self):
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict:
        """Initialize regex patterns for information extraction"""
        return {
            # Arrest Information
            "arrest_date": [
                r"(?:arrested?|arrest date|taken into custody)(?:\s+on)?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"date of arrest:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"arrest:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            ],
            "arrest_time": [
                r"(?:arrested?|arrest time|taken into custody)\s+(?:at|on)?\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
                r"time of arrest:\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
                r"arrest time:\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
            ],
            "arrest_location": [
                r"(?:arrested? at|arrest location|place of arrest)(?:\s+at)?\s+([^\n.;]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way))",
                r"location of arrest:\s*([^\n.;]+)",
                r"arrest location:\s*([^\n.;]+)",
            ],
            "arresting_officer": [
                r"(?:arresting officer|arrested by|officer)(?:\s+name)?:\s*(?:Officer\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)",
                r"Officer\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:arrested|made the arrest)",
                r"(?:by|Officer)\s+([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+),?\s+Badge",
            ],
            "badge_number": [
                r"Badge\s*(?:#|No\.?|Number)?\s*(\d{3,6})",
                r"ID\s*(?:#|No\.?)?\s*(\d{3,6})",
                r"Officer\s+ID:\s*(\d{3,6})",
            ],
            # Charges
            "charges": [
                r"Charge(?:d with|s?):\s*([^\n]+)",
                r"Offense(?:s?):\s*([^\n]+)",
                r"(?:Count|Charge)\s+\d+:\s*([^\n]+)",
                r"Violation of\s+([^\n]+)",
            ],
            "statute_violated": [
                r"(\d+\s+U\.?S\.?C\.?\s+§?\s*\d+(?:\([a-z]\))?)",  # Federal
                r"([A-Z]{2}\s+(?:Penal|Criminal)\s+Code\s+§?\s*\d+\.?\d*)",  # State penal
                r"([A-Z]{2}\s+Stat\.?\s+§?\s*\d+\.?\d*)",  # State statute
            ],
            "charge_degree": [
                r"((?:First|Second|Third|Fourth)-Degree\s+(?:Felony|Misdemeanor))",
                r"(Class\s+[A-D]\s+(?:Felony|Misdemeanor))",
                r"(Felony|Misdemeanor|Infraction|Violation)",
            ],
            # Citation/Ticket Information
            "citation_number": [
                r"(?:Citation|Ticket|Summons)\s*(?:#|No\.?|Number)?\s*([A-Z0-9]{6,15})",
                r"Violation\s*(?:Number|No\.?):\s*([A-Z0-9]{6,15})",
                r"Docket\s*(?:#|No\.?):\s*([A-Z0-9\-]{6,15})",
            ],
            "violation_type": [
                r"Violation:\s*([^\n]+)",
                r"Traffic\s+Violation:\s*([^\n]+)",
                r"Code\s+Violation:\s*([^\n]+)",
            ],
            "fine_amount": [
                r"Fine(?:\s+Amount)?:\s*\$?([\d,]+\.?\d{0,2})",
                r"Total\s+(?:Due|Amount|Fine):\s*\$?([\d,]+\.?\d{0,2})",
                r"Penalty:\s*\$?([\d,]+\.?\d{0,2})",
            ],
            # Tow/Vehicle Information
            "tow_date": [
                r"(?:vehicle\s+)?towed?\s+(?:on|date)?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"tow date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"impound(?:ed)?\s+(?:on|date)?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            ],
            "tow_time": [
                r"towed?\s+(?:at|time)?\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
                r"tow time:\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
            ],
            "tow_company": [
                r"(?:Tow(?:ing)?\s+Company|Towed by):\s*([^\n.;]+)",
                r"Impound(?:ed)?\s+by:\s*([^\n.;]+)",
            ],
            "tow_location": [
                r"(?:Towed? (?:from|to)|Impound(?:ed)? at)(?:\s+to)?\s+([^\n.;]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd))",
                r"(?:Vehicle\s+)?Location:\s*([^\n.;]+)",
            ],
            "vehicle_make_model": [
                r"Vehicle:\s*(\d{4}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
                r"Make/Model:\s*([^\n]+)",
                r"(\d{4}\s+(?:Honda|Toyota|Ford|Chevrolet|Nissan|BMW|Mercedes|Audi|Volkswagen|Hyundai|Kia|Mazda|Subaru|Tesla|Dodge|Jeep|GMC|Ram|Lexus|Acura|Infiniti|Cadillac|Lincoln|Buick)[^\n]+)",
            ],
            "license_plate": [
                r"(?:License Plate|Plate|Tag)(?:\s+#|No\.?)?:\s*([A-Z0-9]{2,8})",
                r"(?:LP|Lic):\s*([A-Z0-9]{2,8})",
                r"Registration:\s*([A-Z0-9]{2,8})",
            ],
            "vin": [
                r"VIN:\s*([A-Z0-9]{17})",
                r"Vehicle\s+ID:\s*([A-Z0-9]{17})",
                r"Serial:\s*([A-Z0-9]{17})",
            ],
            "tow_fee": [
                r"Tow(?:ing)?\s+(?:Fee|Cost|Charge):\s*\$?([\d,]+\.?\d{0,2})",
                r"Storage\s+(?:Fee|Cost):\s*\$?([\d,]+\.?\d{0,2})",
                r"Total\s+(?:Tow\s+)?Fees?:\s*\$?([\d,]+\.?\d{0,2})",
            ],
            # Incident Information
            "incident_number": [
                r"(?:Incident|Case|Report)\s*(?:#|No\.?|Number):\s*([A-Z0-9\-]{6,20})",
                r"IR\s*#?\s*([A-Z0-9\-]{6,20})",
                r"Event\s*(?:#|No\.?):\s*([A-Z0-9\-]{6,20})",
            ],
            "incident_type": [
                r"(?:Incident|Offense)\s+Type:\s*([^\n]+)",
                r"Nature of (?:Call|Incident):\s*([^\n]+)",
                r"Classification:\s*([^\n]+)",
            ],
            "incident_location": [
                r"(?:Incident|Offense)\s+Location:\s*([^\n.;]+)",
                r"Scene:\s*([^\n.;]+)",
                r"Address:\s*([^\n.;]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd))",
            ],
            # People Involved
            "suspect_name": [
                r"(?:Suspect|Defendant|Arrestee)(?:\s+Name)?:\s*([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)",
                r"Name:\s*([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)",
            ],
            "suspect_dob": [
                r"(?:DOB|Date of Birth|Born):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Birth Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            ],
            "suspect_address": [r"(?:Address|Residence):\s*([^\n.;]+)", r"Lives at:\s*([^\n.;]+)"],
            "victim_name": [r"Victim(?:\s+Name)?:\s*([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)"],
            "witness_names": [
                r"Witness(?:es)?(?:\s+Name)?:\s*([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)",
                r"Witness\s+\d+:\s*([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)",
            ],
            # Court Information
            "court_date": [
                r"(?:Court|Hearing)\s+Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Scheduled for:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Appearance\s+Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            ],
            "court_time": [
                r"(?:Court|Hearing)\s+Time:\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
                r"Scheduled at:\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
            ],
            "court_location": [
                r"Court(?:house)?(?:\s+Location)?:\s*([^\n.;]+)",
                r"Venue:\s*([^\n.;]+)",
            ],
            "docket_number": [
                r"Docket(?:\s+#|No\.?|Number):\s*([A-Z0-9\-]{6,20})",
                r"Case\s+#:\s*([A-Z0-9\-]{6,20})",
            ],
            # Bail/Bond Information
            "bail_amount": [
                r"Bail(?:\s+Amount)?:\s*\$?([\d,]+\.?\d{0,2})",
                r"Bond:\s*\$?([\d,]+\.?\d{0,2})",
            ],
            "bail_status": [
                r"Bail\s+Status:\s*([^\n]+)",
                r"(Released on (?:own recognizance|OR|bail|bond))",
                r"(Held (?:without bail|on [\d,]+ bail))",
            ],
        }

    def analyze_document(self, content: str, filename: str = "") -> Dict[str, Any]:
        """
        Analyze PDF discovery document and extract all legal information

        Args:
            content: Text content from PDF
            filename: Original filename (optional)

        Returns:
            Comprehensive dictionary of extracted information
        """
        results = {
            "filename": filename,
            "analyzed_at": datetime.utcnow().isoformat(),
            "document_type": self._determine_document_type(content),
            "arrest_information": self._extract_arrest_info(content),
            "charges": self._extract_charges(content),
            "citation_information": self._extract_citation_info(content),
            "tow_information": self._extract_tow_info(content),
            "vehicle_information": self._extract_vehicle_info(content),
            "incident_information": self._extract_incident_info(content),
            "people_involved": self._extract_people_info(content),
            "court_information": self._extract_court_info(content),
            "timeline": self._build_timeline(content),
            "summary": "",
            "metadata": {
                "total_pages": self._estimate_pages(content),
                "word_count": len(content.split()),
                "has_photos": bool(re.search(r"photo|image|exhibit\s+[A-Z0-9]+", content, re.I)),
                "has_signatures": bool(re.search(r"signature|signed|sworn", content, re.I)),
            },
        }

        # Generate human-readable summary
        results["summary"] = self._generate_summary(results)

        return results

    def _determine_document_type(self, content: str) -> str:
        """Determine the type of legal document"""
        content_lower = content.lower()

        if any(word in content_lower for word in ["arrest", "booking", "custody"]):
            return "Arrest Report"
        elif any(
            word in content_lower for word in ["citation", "ticket", "summons", "traffic violation"]
        ):
            return "Citation/Ticket"
        elif any(word in content_lower for word in ["tow", "impound", "vehicle storage"]):
            return "Tow/Impound Record"
        elif any(word in content_lower for word in ["police report", "incident report", "ir #"]):
            return "Police/Incident Report"
        elif any(word in content_lower for word in ["discovery", "disclosure"]):
            return "Discovery Document"
        elif any(
            word in content_lower for word in ["charging document", "information", "indictment"]
        ):
            return "Charging Document"
        elif any(word in content_lower for word in ["court order", "judgment", "ruling"]):
            return "Court Document"
        else:
            return "Unknown Document Type"

    def _extract_with_patterns(
        self, content: str, pattern_list: List[str], extract_all: bool = False
    ) -> Optional[str] | List[str]:
        """Extract information using list of regex patterns"""
        results = []

        for pattern in pattern_list:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                value = match.group(1).strip()
                if value:
                    results.append(value)

        if not results:
            return [] if extract_all else None

        if extract_all:
            return list(set(results))  # Remove duplicates
        else:
            return results[0]  # Return first match

    def _extract_arrest_info(self, content: str) -> Dict:
        """Extract arrest-specific information"""
        return {
            "arrest_date": self._extract_with_patterns(content, self.patterns["arrest_date"]),
            "arrest_time": self._extract_with_patterns(content, self.patterns["arrest_time"]),
            "arrest_location": self._extract_with_patterns(
                content, self.patterns["arrest_location"]
            ),
            "arresting_officer": self._extract_with_patterns(
                content, self.patterns["arresting_officer"]
            ),
            "badge_number": self._extract_with_patterns(content, self.patterns["badge_number"]),
            "was_arrested": bool(re.search(r"\barrest(?:ed)?\b", content, re.I)),
        }

    def _extract_charges(self, content: str) -> Dict:
        """Extract criminal charges information"""
        charges_list = self._extract_with_patterns(
            content, self.patterns["charges"], extract_all=True
        )
        statutes = self._extract_with_patterns(
            content, self.patterns["statute_violated"], extract_all=True
        )
        degrees = self._extract_with_patterns(
            content, self.patterns["charge_degree"], extract_all=True
        )

        return {
            "charges": charges_list,
            "statutes_violated": statutes,
            "charge_degrees": degrees,
            "total_charges": len(charges_list) if charges_list else 0,
        }

    def _extract_citation_info(self, content: str) -> Dict:
        """Extract citation/ticket information"""
        return {
            "citation_number": self._extract_with_patterns(
                content, self.patterns["citation_number"]
            ),
            "violation_type": self._extract_with_patterns(content, self.patterns["violation_type"]),
            "fine_amount": self._extract_with_patterns(content, self.patterns["fine_amount"]),
            "is_citation": bool(re.search(r"\b(?:citation|ticket|summons)\b", content, re.I)),
        }

    def _extract_tow_info(self, content: str) -> Dict:
        """Extract tow/impound information"""
        return {
            "tow_date": self._extract_with_patterns(content, self.patterns["tow_date"]),
            "tow_time": self._extract_with_patterns(content, self.patterns["tow_time"]),
            "tow_company": self._extract_with_patterns(content, self.patterns["tow_company"]),
            "tow_location": self._extract_with_patterns(content, self.patterns["tow_location"]),
            "tow_fee": self._extract_with_patterns(content, self.patterns["tow_fee"]),
            "was_towed": bool(re.search(r"\b(?:tow(?:ed)?|impound(?:ed)?)\b", content, re.I)),
        }

    def _extract_vehicle_info(self, content: str) -> Dict:
        """Extract vehicle information"""
        return {
            "make_model": self._extract_with_patterns(content, self.patterns["vehicle_make_model"]),
            "license_plate": self._extract_with_patterns(content, self.patterns["license_plate"]),
            "vin": self._extract_with_patterns(content, self.patterns["vin"]),
            "has_vehicle_info": bool(
                re.search(r"\b(?:vehicle|car|truck|motorcycle)\b", content, re.I)
            ),
        }

    def _extract_incident_info(self, content: str) -> Dict:
        """Extract incident/case information"""
        return {
            "incident_number": self._extract_with_patterns(
                content, self.patterns["incident_number"]
            ),
            "incident_type": self._extract_with_patterns(content, self.patterns["incident_type"]),
            "incident_location": self._extract_with_patterns(
                content, self.patterns["incident_location"]
            ),
        }

    def _extract_people_info(self, content: str) -> Dict:
        """Extract information about people involved"""
        return {
            "suspect": {
                "name": self._extract_with_patterns(content, self.patterns["suspect_name"]),
                "dob": self._extract_with_patterns(content, self.patterns["suspect_dob"]),
                "address": self._extract_with_patterns(content, self.patterns["suspect_address"]),
            },
            "victim": {"name": self._extract_with_patterns(content, self.patterns["victim_name"])},
            "witnesses": self._extract_with_patterns(
                content, self.patterns["witness_names"], extract_all=True
            ),
            "officers": self._extract_with_patterns(
                content, self.patterns["arresting_officer"], extract_all=True
            ),
        }

    def _extract_court_info(self, content: str) -> Dict:
        """Extract court-related information"""
        return {
            "court_date": self._extract_with_patterns(content, self.patterns["court_date"]),
            "court_time": self._extract_with_patterns(content, self.patterns["court_time"]),
            "court_location": self._extract_with_patterns(content, self.patterns["court_location"]),
            "docket_number": self._extract_with_patterns(content, self.patterns["docket_number"]),
            "bail_amount": self._extract_with_patterns(content, self.patterns["bail_amount"]),
            "bail_status": self._extract_with_patterns(content, self.patterns["bail_status"]),
        }

    def _build_timeline(self, content: str) -> List[Dict]:
        """Build chronological timeline of events"""
        timeline = []

        # Extract all dates and associated events
        date_pattern = r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})(?:\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?))?\s*[:-]?\s*([^\n.;]{10,100})"

        matches = re.finditer(date_pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            date_str = match.group(1)
            time_str = match.group(2) if match.group(2) else "Unknown time"
            event = match.group(3).strip() if len(match.groups()) > 2 else "Event"

            timeline.append(
                {"date": date_str, "time": time_str, "event": event[:100]}  # Limit length
            )

        # Sort by date (basic sorting, can be improved)
        return timeline[:20]  # Limit to 20 events

    def _estimate_pages(self, content: str) -> int:
        """Estimate number of pages based on content"""
        # Rough estimate: 3000 characters per page
        return max(1, len(content) // 3000)

    def _generate_summary(self, results: Dict) -> str:
        """Generate human-readable summary of findings"""
        summary_parts = []

        # Document type
        summary_parts.append(f"Document Type: {results['document_type']}")

        # Arrest info
        arrest = results["arrest_information"]
        if arrest["was_arrested"]:
            arrest_details = f"Arrest on {arrest['arrest_date'] or 'unknown date'}"
            if arrest["arrest_time"]:
                arrest_details += f" at {arrest['arrest_time']}"
            if arrest["arrest_location"]:
                arrest_details += f" at {arrest['arrest_location']}"
            if arrest["arresting_officer"]:
                arrest_details += f" by Officer {arrest['arresting_officer']}"
            summary_parts.append(arrest_details)

        # Charges
        charges = results["charges"]
        if charges["total_charges"] > 0:
            summary_parts.append(f"Charges: {charges['total_charges']} count(s)")
            if charges["charges"]:
                summary_parts.append(f"  - {', '.join(charges['charges'][:3])}")

        # Citation
        citation = results["citation_information"]
        if citation["is_citation"]:
            citation_details = f"Citation #{citation['citation_number'] or 'N/A'}"
            if citation["fine_amount"]:
                citation_details += f" - Fine: ${citation['fine_amount']}"
            summary_parts.append(citation_details)

        # Tow
        tow = results["tow_information"]
        if tow["was_towed"]:
            tow_details = f"Vehicle towed on {tow['tow_date'] or 'unknown date'}"
            if tow["tow_company"]:
                tow_details += f" by {tow['tow_company']}"
            if tow["tow_fee"]:
                tow_details += f" - Fee: ${tow['tow_fee']}"
            summary_parts.append(tow_details)

        # Vehicle
        vehicle = results["vehicle_information"]
        if vehicle["has_vehicle_info"]:
            vehicle_details = f"Vehicle: {vehicle['make_model'] or 'Unknown'}"
            if vehicle["license_plate"]:
                vehicle_details += f" (Plate: {vehicle['license_plate']})"
            summary_parts.append(vehicle_details)

        # Court
        court = results["court_information"]
        if court["court_date"]:
            court_details = f"Court Date: {court['court_date']}"
            if court["court_time"]:
                court_details += f" at {court['court_time']}"
            if court["court_location"]:
                court_details += f" - {court['court_location']}"
            summary_parts.append(court_details)

        # Timeline
        if results["timeline"]:
            summary_parts.append(f"Timeline: {len(results['timeline'])} events identified")

        # People
        people = results["people_involved"]
        if people["suspect"]["name"]:
            summary_parts.append(f"Suspect: {people['suspect']['name']}")
        if people["witnesses"]:
            summary_parts.append(f"Witnesses: {len(people['witnesses'])} identified")

        return "\n".join(summary_parts) if summary_parts else "No significant information extracted"

    def export_to_json(self, results: Dict, filepath: str):
        """Export analysis results to JSON file"""
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

    def export_to_report(self, results: Dict) -> str:
        """Generate formatted text report"""
        report = []
        report.append("=" * 80)
        report.append("PDF DISCOVERY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Analyzed: {results['analyzed_at']}")
        report.append(f"Filename: {results['filename']}")
        report.append(f"Document Type: {results['document_type']}")
        report.append("")

        report.append("-" * 80)
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(results["summary"])
        report.append("")

        # Detailed sections
        if results["arrest_information"]["was_arrested"]:
            report.append("-" * 80)
            report.append("ARREST INFORMATION")
            report.append("-" * 80)
            for key, value in results["arrest_information"].items():
                if value and key != "was_arrested":
                    report.append(f"  {key.replace('_', ' ').title()}: {value}")
            report.append("")

        if results["charges"]["total_charges"] > 0:
            report.append("-" * 80)
            report.append("CHARGES")
            report.append("-" * 80)
            for i, charge in enumerate(results["charges"]["charges"], 1):
                report.append(f"  {i}. {charge}")
            report.append("")

        if results["tow_information"]["was_towed"]:
            report.append("-" * 80)
            report.append("TOW/IMPOUND INFORMATION")
            report.append("-" * 80)
            for key, value in results["tow_information"].items():
                if value and key != "was_towed":
                    report.append(f"  {key.replace('_', ' ').title()}: {value}")
            report.append("")

        if results["timeline"]:
            report.append("-" * 80)
            report.append("TIMELINE OF EVENTS")
            report.append("-" * 80)
            for event in results["timeline"][:10]:
                report.append(f"  {event['date']} {event['time']} - {event['event']}")
            report.append("")

        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)

        return "\n".join(report)


# Usage example
if __name__ == "__main__":
    # Example usage
    analyzer = PDFDiscoveryAnalyzer()

    # Sample PDF content (in production, extract from actual PDF)
    sample_content = """
    ARREST REPORT
    
    Incident #: IR-2024-12345
    Date of Arrest: 03/15/2024
    Time of Arrest: 2:30 PM
    Location: 123 Main Street, Cityville
    
    Arresting Officer: Officer John Smith
    Badge #: 4567
    
    Suspect: Michael Johnson
    DOB: 05/22/1985
    Address: 456 Oak Avenue, Cityville
    
    Charges:
    Count 1: Driving Under the Influence (DUI)
    Count 2: Resisting Arrest
    Violation of NJ Penal Code § 39:4-50
    
    Vehicle: 2018 Honda Accord
    License Plate: ABC1234
    VIN: 1HGBH41JXMN109186
    
    Vehicle towed on 03/15/2024 at 3:45 PM
    Tow Company: Quick Tow Services
    Tow Fee: $350.00
    Storage Fee: $50.00/day
    
    Court Date: 04/20/2024
    Court Time: 9:00 AM
    Court Location: Cityville Municipal Court
    Docket #: 2024-TR-5678
    
    Bail: $2,500.00
    Status: Released on bail
    """

    results = analyzer.analyze_document(sample_content, "arrest_report_2024.pdf")

    # Print formatted report
    print(analyzer.export_to_report(results))

    # Save JSON
    # analyzer.export_to_json(results, "analysis_results.json")
