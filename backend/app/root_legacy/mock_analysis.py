"""
Mock Analysis Generator
Generates realistic BWC analysis results without AI dependencies
Used when Whisper/AI tools are not available
"""

import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class MockAnalysisGenerator:
    """Generate mock analysis results for testing and demos"""

    SAMPLE_SPEAKERS = ["OFFICER_01", "OFFICER_02", "CIVILIAN", "DISPATCHER"]

    SAMPLE_PHRASES = [
        "Step out of the vehicle please",
        "Do you know why I pulled you over today",
        "License and registration please",
        "I need you to keep your hands where I can see them",
        "Are you carrying any weapons",
        "Have you had anything to drink tonight",
        "I'm going to need you to step back",
        "Can you tell me what happened",
        "What's your name and date of birth",
        "Stay right here, I'll be right back",
        "I didn't do anything wrong",
        "I was just going to the store",
        "Am I being detained",
        "I want to speak to a lawyer",
        "This is not fair",
        "I have a right to know what I'm being charged with",
        "Dispatch, I need backup at this location",
        "Run a check on plate number",
        "Subject is being cooperative",
        "Requesting EMT to the scene",
    ]

    SAMPLE_ENTITIES = {
        "persons": ["John Smith", "Officer Johnson", "Detective Williams", "Sarah Martinez"],
        "locations": [
            "Main Street",
            "123 Oak Avenue",
            "Central Police Station",
            "County Courthouse",
        ],
        "organizations": ["Metro PD", "State Police", "County Sheriff", "District Attorney"],
        "dates": ["January 15, 2024", "March 22, 2024", "February 10, 2024"],
    }

    def generate_mock_transcript(self, duration_seconds: int = 180) -> List[Dict]:
        """Generate mock transcript segments"""
        segments = []
        current_time = 0.0
        segment_id = 0

        while current_time < duration_seconds:
            segment_duration = random.uniform(2.0, 8.0)
            speaker = random.choice(self.SAMPLE_SPEAKERS)
            text = random.choice(self.SAMPLE_PHRASES)

            segment = {
                "id": segment_id,
                "start_time": round(current_time, 2),
                "end_time": round(current_time + segment_duration, 2),
                "duration": round(segment_duration, 2),
                "speaker": speaker,
                "speaker_label": self._get_speaker_label(speaker),
                "text": text,
                "confidence": round(random.uniform(0.85, 0.99), 3),
                "words": self._generate_words(text, current_time, segment_duration),
            }

            segments.append(segment)
            current_time += segment_duration + random.uniform(0.5, 2.0)  # Add pause
            segment_id += 1

        return segments

    def _get_speaker_label(self, speaker: str) -> str:
        """Convert speaker ID to human-readable label"""
        labels = {
            "OFFICER_01": "Primary Officer",
            "OFFICER_02": "Backup Officer",
            "CIVILIAN": "Subject",
            "DISPATCHER": "Radio Dispatch",
        }
        return labels.get(speaker, speaker)

    def _generate_words(self, text: str, start_time: float, duration: float) -> List[Dict]:
        """Generate word-level timestamps"""
        words = text.split()
        word_duration = duration / len(words) if words else 0

        word_segments = []
        current_pos = start_time

        for word in words:
            word_segments.append(
                {
                    "word": word,
                    "start": round(current_pos, 2),
                    "end": round(current_pos + word_duration, 2),
                    "probability": round(random.uniform(0.9, 0.99), 3),
                }
            )
            current_pos += word_duration

        return word_segments

    def generate_mock_entities(self) -> Dict[str, List[Dict]]:
        """Generate mock extracted entities"""
        entities = {}

        for entity_type, samples in self.SAMPLE_ENTITIES.items():
            count = random.randint(2, len(samples))
            selected = random.sample(samples, count)

            entities[entity_type] = [
                {
                    "text": item,
                    "type": entity_type.rstrip("s").upper(),
                    "confidence": round(random.uniform(0.85, 0.98), 3),
                    "mentions": random.randint(1, 5),
                }
                for item in selected
            ]

        return entities

    def generate_mock_discrepancies(self) -> List[Dict]:
        """Generate mock discrepancy reports"""
        discrepancies = [
            {
                "id": 1,
                "type": "timeline",
                "severity": "high",
                "description": "Officer stated subject was reaching for waistband at 00:45, but video shows hands visible at steering wheel",
                "timestamp": 45.2,
                "source_conflict": ["body_camera", "police_report"],
                "recommendation": "Review video evidence carefully and clarify report narrative",
            },
            {
                "id": 2,
                "type": "statement",
                "severity": "medium",
                "description": "Subject claims no verbal warning given, audio shows warning at 01:23",
                "timestamp": 83.1,
                "source_conflict": ["audio_transcript", "civilian_statement"],
                "recommendation": "Cross-reference with witness statements",
            },
            {
                "id": 3,
                "type": "procedure",
                "severity": "low",
                "description": "Miranda rights read at 02:15, slightly delayed from recommended protocol",
                "timestamp": 135.8,
                "source_conflict": ["procedure_guidelines", "body_camera"],
                "recommendation": "Document timing justification in supplemental report",
            },
        ]

        return random.sample(discrepancies, random.randint(1, 3))

    def generate_mock_timeline(self, duration: int) -> List[Dict]:
        """Generate mock timeline events"""
        events = []
        timestamps = sorted([random.uniform(0, duration) for _ in range(random.randint(5, 12))])

        event_types = [
            ("Initial Contact", "Officer approaches vehicle"),
            ("License Request", "Officer requests license and registration"),
            ("Verbal Exchange", "Discussion with subject"),
            ("Radio Communication", "Officer contacts dispatch"),
            ("Search Conducted", "Vehicle search performed"),
            ("Subject Detained", "Subject placed in custody"),
            ("Miranda Rights", "Rights read to subject"),
            ("Transport", "Subject transported to station"),
        ]

        for i, timestamp in enumerate(timestamps):
            if i < len(event_types):
                event_type, description = event_types[i]
            else:
                event_type, description = random.choice(event_types)

            events.append(
                {
                    "timestamp": round(timestamp, 2),
                    "type": event_type,
                    "description": description,
                    "source": random.choice(["BWC Video", "Audio Transcript", "Police Report"]),
                }
            )

        return events

    def generate_complete_analysis(
        self, video_path: str, case_number: str = None, evidence_number: str = None
    ) -> Dict:
        """Generate a complete mock analysis report"""

        # Simulate file analysis
        file_size = Path(video_path).stat().st_size if Path(video_path).exists() else 50000000

        # Calculate mock video duration (estimate based on file size)
        duration = int(file_size / 500000)  # Rough estimate
        duration = max(60, min(duration, 600))  # Clamp between 1-10 minutes

        transcript = self.generate_mock_transcript(duration)
        entities = self.generate_mock_entities()
        discrepancies = self.generate_mock_discrepancies()
        timeline = self.generate_mock_timeline(duration)

        report = {
            "metadata": {
                "analysis_type": "BWC Forensic Analysis",
                "version": "1.0.0 (Mock)",
                "generated_at": datetime.utcnow().isoformat(),
                "case_number": case_number or "MOCK-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
                "evidence_number": evidence_number or "EV-" + str(random.randint(1000, 9999)),
                "video_file": Path(video_path).name,
                "file_size": file_size,
                "duration": duration,
                "analysis_mode": "mock_demo",
            },
            "chain_of_custody": {
                "sha256_hash": hashlib.sha256(str(random.random()).encode()).hexdigest(),
                "acquired_at": (
                    datetime.utcnow() - timedelta(days=random.randint(1, 30))
                ).isoformat(),
                "acquired_by": "Evidence Custodian",
                "source": "Department Records",
                "verification_method": "SHA-256 cryptographic hash",
            },
            "transcript": {
                "total_segments": len(transcript),
                "total_duration": duration,
                "speakers": list(set(s["speaker"] for s in transcript)),
                "segments": transcript,
            },
            "entities": entities,
            "discrepancies": {
                "total": len(discrepancies),
                "by_severity": {
                    "high": len([d for d in discrepancies if d["severity"] == "high"]),
                    "medium": len([d for d in discrepancies if d["severity"] == "medium"]),
                    "low": len([d for d in discrepancies if d["severity"] == "low"]),
                },
                "items": discrepancies,
            },
            "timeline": timeline,
            "summary": {
                "total_duration": duration,
                "total_speakers": len(set(s["speaker"] for s in transcript)),
                "total_segments": len(transcript),
                "total_discrepancies": len(discrepancies),
                "critical_findings": len([d for d in discrepancies if d["severity"] == "high"]),
                "entities_extracted": sum(len(v) for v in entities.values()),
                "analysis_complete": True,
            },
        }

        return report


# Global instance
mock_generator = MockAnalysisGenerator()
