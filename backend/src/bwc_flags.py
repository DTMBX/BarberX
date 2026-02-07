import re
from dataclasses import dataclass


@dataclass
class ReviewFlag:
    pov_id: int
    start_time: float
    end_time: float
    excerpt: str
    rule_id: str


# Simple lexicons (expandable)
PROFANITY_LEXICON = {"fuck", "shit", "bitch", "asshole"}
FORCE_PHRASES = {
    "use of force": "force_use",
    "taser": "force_taser",
    "firearm": "force_firearm",
}
PROCEDURAL_PHRASES = {
    "step out": "proc_step_out",
    "you're under arrest": "proc_under_arrest",
    "stop resisting": "proc_stop_resisting",
    "put your hands": "proc_put_hands",
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def detect_profanity(transcript_segments: list[dict], pov_id: int) -> list[ReviewFlag]:
    flags = []
    for seg in transcript_segments:
        tokens = _tokenize(seg.get("text", ""))
        hits = PROFANITY_LEXICON.intersection(tokens)
        if hits:
            flags.append(
                ReviewFlag(
                    pov_id=pov_id,
                    start_time=seg.get("start_time", 0.0),
                    end_time=seg.get("end_time", 0.0),
                    excerpt=seg.get("text", "")[:240],
                    rule_id="profanity",
                )
            )
    return flags


def detect_phrases(transcript_segments: list[dict], pov_id: int) -> list[ReviewFlag]:
    flags = []
    for seg in transcript_segments:
        text = seg.get("text", "").lower()
        for phrase, rule in {**FORCE_PHRASES, **PROCEDURAL_PHRASES}.items():
            if phrase in text:
                flags.append(
                    ReviewFlag(
                        pov_id=pov_id,
                        start_time=seg.get("start_time", 0.0),
                        end_time=seg.get("end_time", 0.0),
                        excerpt=seg.get("text", "")[:240],
                        rule_id=rule,
                    )
                )
    return flags


def analyze_transcript_for_flags(all_transcripts: list[list[dict]]) -> list[ReviewFlag]:
    """all_transcripts: list per-POV, where each item is a list of segment dicts with start_time,end_time,text"""
    review_flags = []
    for pov_index, segments in enumerate(all_transcripts):
        review_flags.extend(detect_profanity(segments, pov_index))
        review_flags.extend(detect_phrases(segments, pov_index))

    return review_flags
