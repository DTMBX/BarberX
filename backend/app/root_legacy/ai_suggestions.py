# AI Auto-Complete and Smart Suggestions
import random
import re
from datetime import datetime


class SmartSuggestionEngine:
    """AI-powered suggestion engine for forms and inputs"""

    def __init__(self):
        # Training data (replace with actual ML model)
        self.common_descriptions = [
            "Officer conducted traffic stop for speeding violation",
            "Suspect apprehended during routine patrol",
            "Domestic disturbance call responded to",
            "Use of force incident during arrest",
            "Evidence collected from crime scene",
            "Witness interview conducted",
            "Body worn camera footage from incident",
            "Dashboard camera recording of pursuit",
            "Interview recording with suspect",
            "Crime scene photography documentation",
        ]

        self.evidence_types = {
            "video": ["BWC", "Dashboard Camera", "Surveillance", "Interview", "Traffic Stop"],
            "audio": ["Interview", "Phone Call", "911 Recording", "Radio Traffic"],
            "document": ["Police Report", "Witness Statement", "Medical Report", "Lab Results"],
            "image": ["Crime Scene Photo", "Evidence Photo", "Mugshot", "Diagram"],
        }

        self.priority_keywords = {
            "critical": ["shooting", "death", "fatal", "officer-involved", "homicide", "weapon"],
            "high": ["assault", "robbery", "burglary", "domestic", "use of force", "injury"],
            "normal": ["traffic", "theft", "vandalism", "trespassing", "complaint"],
            "low": ["parking", "noise", "minor", "citation", "warning"],
        }

    def suggest_description(self, partial_text):
        """Suggest description completions based on partial text"""
        if not partial_text or len(partial_text) < 3:
            return []

        partial_lower = partial_text.lower()
        suggestions = []

        # Find matching descriptions
        for desc in self.common_descriptions:
            if partial_lower in desc.lower():
                suggestions.append({"text": desc, "confidence": 0.85, "source": "template"})

        # Generate smart completions
        if "officer" in partial_lower:
            suggestions.extend(
                [
                    {
                        "text": "Officer conducted routine patrol in district",
                        "confidence": 0.75,
                        "source": "ai",
                    },
                    {
                        "text": "Officer responded to dispatch call",
                        "confidence": 0.72,
                        "source": "ai",
                    },
                ]
            )

        if "traffic" in partial_lower:
            suggestions.extend(
                [
                    {
                        "text": "Traffic stop conducted for moving violation",
                        "confidence": 0.80,
                        "source": "ai",
                    },
                    {
                        "text": "Traffic incident resulting in citation",
                        "confidence": 0.78,
                        "source": "ai",
                    },
                ]
            )

        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:5]

    def suggest_priority(self, description):
        """Suggest priority level based on description"""
        description_lower = description.lower()

        # Check for keywords
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    confidence = 0.70 + (random.random() * 0.25)  # 70-95%
                    return {
                        "priority": priority,
                        "confidence": round(confidence, 2),
                        "reason": f'Detected keyword: "{keyword}"',
                    }

        # Default to normal
        return {"priority": "normal", "confidence": 0.50, "reason": "No priority keywords detected"}

    def suggest_tags(self, description, evidence_type=None):
        """Extract and suggest relevant tags"""
        description_lower = description.lower()
        tags = []

        # Common tags
        tag_mapping = {
            "traffic": ["traffic-stop", "moving-violation"],
            "use of force": ["use-of-force", "officer-involved"],
            "domestic": ["domestic-violence", "family-dispute"],
            "weapon": ["weapon", "firearm"],
            "injury": ["injury", "medical"],
            "arrest": ["arrest", "custody"],
            "pursuit": ["vehicle-pursuit", "chase"],
            "interview": ["interview", "interrogation"],
            "bwc": ["body-camera", "video-evidence"],
            "dash": ["dashboard-camera", "vehicle-camera"],
        }

        for keyword, tag_list in tag_mapping.items():
            if keyword in description_lower:
                tags.extend(tag_list)

        # Evidence type tags
        if evidence_type:
            if "video" in evidence_type.lower():
                tags.append("video-evidence")
            elif "audio" in evidence_type.lower():
                tags.append("audio-evidence")
            elif "document" in evidence_type.lower():
                tags.append("document")

        # Remove duplicates
        tags = list(set(tags))

        return {"tags": tags[:8], "confidence": 0.80 if tags else 0.30}  # Max 8 tags

    def auto_categorize(self, filename, description=""):
        """Automatically categorize evidence based on filename and description"""
        filename_lower = filename.lower()
        description_lower = description.lower()

        # Detect evidence type
        evidence_type = "unknown"

        # Video extensions
        if any(ext in filename_lower for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]):
            evidence_type = "video"

            # Specific video type
            if "bwc" in filename_lower or "body" in filename_lower:
                subtype = "BWC"
            elif "dash" in filename_lower or "vehicle" in filename_lower:
                subtype = "Dashboard Camera"
            elif "interview" in filename_lower or description_lower:
                subtype = "Interview"
            else:
                subtype = "Surveillance"

        # Audio extensions
        elif any(ext in filename_lower for ext in [".mp3", ".wav", ".m4a", ".aac"]):
            evidence_type = "audio"
            subtype = "Audio Recording"

        # Document extensions
        elif any(ext in filename_lower for ext in [".pdf", ".doc", ".docx", ".txt"]):
            evidence_type = "document"
            subtype = "Document"

        # Image extensions
        elif any(ext in filename_lower for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]):
            evidence_type = "image"
            subtype = "Photo"

        else:
            subtype = "Other"

        # Calculate confidence
        confidence = 0.95 if evidence_type != "unknown" else 0.30

        return {"evidence_type": evidence_type, "subtype": subtype, "confidence": confidence}

    def suggest_case_number(self, existing_cases=[]):
        """Generate suggested case number"""
        year = datetime.now().year
        month = datetime.now().month

        # Find highest case number for this month
        pattern = f"CR-{year}-{month:02d}"

        # Mock logic (replace with database query)
        last_number = len(existing_cases) + 1

        return {
            "case_number": f"{pattern}-{last_number:04d}",
            "pattern": pattern,
            "confidence": 0.90,
        }

    def analyze_text_sentiment(self, text):
        """Analyze sentiment of text (positive, neutral, negative)"""
        # Simple keyword-based sentiment analysis
        positive_words = ["resolved", "cooperative", "compliant", "successful", "peaceful"]
        negative_words = ["violent", "aggressive", "resistant", "confrontational", "hostile"]

        text_lower = text.lower()

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            sentiment = "positive"
            score = 0.70 + (pos_count * 0.05)
        elif neg_count > pos_count:
            sentiment = "negative"
            score = -(0.70 + (neg_count * 0.05))
        else:
            sentiment = "neutral"
            score = 0.0

        return {"sentiment": sentiment, "score": round(score, 2), "confidence": 0.65}

    def suggest_similar_cases(self, description, limit=5):
        """Find similar cases based on description"""
        # Mock implementation (replace with actual similarity search)
        similar_cases = [
            {
                "case_id": "CR-2026-001234",
                "similarity": 0.87,
                "description": "Traffic stop resulting in arrest",
                "outcome": "Conviction",
            },
            {
                "case_id": "CR-2026-001189",
                "similarity": 0.82,
                "description": "Vehicle pursuit and apprehension",
                "outcome": "Plea Deal",
            },
            {
                "case_id": "CR-2026-001156",
                "similarity": 0.78,
                "description": "Traffic violation and citation",
                "outcome": "Citation Paid",
            },
        ]

        return similar_cases[:limit]

    def predict_processing_time(self, priority, evidence_type, description=""):
        """Predict how long processing will take"""
        # Base times by priority (in hours)
        base_times = {"critical": 4, "high": 24, "normal": 72, "low": 168}

        # Complexity factors
        complexity = 1.0

        if evidence_type == "video":
            complexity *= 1.5  # Video takes longer

        if len(description) > 500:
            complexity *= 1.2  # More complex cases

        if "multiple" in description.lower():
            complexity *= 1.3  # Multiple items

        estimated_hours = base_times.get(priority, 72) * complexity

        return {
            "estimated_hours": round(estimated_hours, 1),
            "estimated_days": round(estimated_hours / 24, 1),
            "confidence": 0.75,
        }


# Export singleton instance
smart_suggest = SmartSuggestionEngine()
