"""
Body-Worn Camera (BWC) Forensic Analysis Service
Court-Defensible Video Evidence Processing for Civil Rights Litigation

This service provides comprehensive analysis of police body-worn camera footage
with features specifically designed for court admissibility under Federal Rules
of Evidence 901(b)(9) and state equivalents.

Features:
- Chain of custody tracking (SHA-256 checksums)
- Multi-modal analysis (audio, video, metadata)
- Timeline synchronization with CAD logs and police reports
- Speaker diarization (officer vs civilian)
- Audio transcription with word-level timestamps
- Scene analysis and object detection
- Discrepancy detection across evidence sources
- Court-ready reporting with citations

Author: Evident Legal Tech Platform
License: MIT
"""

import hashlib
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import spacy
import torch
import whisper
from pyannote.audio import Pipeline
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ChainOfCustody:
    """Chain of custody record for evidence file"""

    file_path: str
    sha256_hash: str
    file_size: int
    created_at: datetime
    modified_at: datetime
    acquired_at: datetime
    acquired_by: str
    source: str  # "OPRA request", "Discovery production", etc.
    verification_method: str = "SHA-256 cryptographic hash"

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "sha256_hash": self.sha256_hash,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "acquired_at": self.acquired_at.isoformat(),
            "acquired_by": self.acquired_by,
            "source": self.source,
            "verification_method": self.verification_method,
        }


@dataclass
class TranscriptSegment:
    """Single segment of transcribed audio with speaker attribution"""

    start_time: float
    end_time: float
    text: str
    speaker: Optional[str] = None  # "SPEAKER_00", "SPEAKER_01", etc.
    speaker_label: Optional[str] = None  # "Officer Smith", "Civilian", etc.
    confidence: float = 1.0
    words: List[Dict] = field(default_factory=list)

    def duration(self) -> float:
        return self.end_time - self.start_time

    def to_dict(self) -> Dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration(),
            "text": self.text,
            "speaker": self.speaker,
            "speaker_label": self.speaker_label,
            "confidence": self.confidence,
            "words": self.words,
        }


@dataclass
class DiscrepancyReport:
    """Detected discrepancy between evidence sources"""

    discrepancy_type: str  # "timing", "statement", "event", "identification"
    severity: str  # "critical", "major", "minor"
    bwc_evidence: str
    conflicting_evidence: str
    conflicting_source: str  # "CAD log", "Police report", "Officer statement"
    timestamp: Optional[float] = None
    description: str = ""
    legal_significance: str = ""

    def to_dict(self) -> Dict:
        return {
            "type": self.discrepancy_type,
            "severity": self.severity,
            "bwc_evidence": self.bwc_evidence,
            "conflicting_evidence": self.conflicting_evidence,
            "conflicting_source": self.conflicting_source,
            "timestamp": self.timestamp,
            "description": self.description,
            "legal_significance": self.legal_significance,
        }


@dataclass
class BWCAnalysisReport:
    """Comprehensive BWC analysis report for court review"""

    file_name: str
    file_hash: str
    analysis_date: datetime
    duration: float

    # Chain of custody
    chain_of_custody: ChainOfCustody

    # Audio analysis
    transcript: List[TranscriptSegment] = field(default_factory=list)
    speakers: Dict[str, str] = field(default_factory=dict)  # speaker_id -> label

    # Video analysis
    scenes: List[Dict] = field(default_factory=list)
    objects_detected: List[Dict] = field(default_factory=list)

    # Metadata
    metadata: Dict = field(default_factory=dict)

    # Cross-reference analysis
    timeline_events: List[Dict] = field(default_factory=list)
    discrepancies: List[DiscrepancyReport] = field(default_factory=list)

    # Entities extracted
    entities: Dict[str, List[str]] = field(default_factory=dict)

    # Court documentation
    evidence_number: Optional[str] = None
    case_number: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "file_name": self.file_name,
            "file_hash": self.file_hash,
            "analysis_date": self.analysis_date.isoformat(),
            "duration": self.duration,
            "chain_of_custody": self.chain_of_custody.to_dict(),
            "transcript": [seg.to_dict() for seg in self.transcript],
            "speakers": self.speakers,
            "scenes": self.scenes,
            "objects_detected": self.objects_detected,
            "metadata": self.metadata,
            "timeline_events": self.timeline_events,
            "discrepancies": [d.to_dict() for d in self.discrepancies],
            "entities": self.entities,
            "evidence_number": self.evidence_number,
            "case_number": self.case_number,
            "analysis_summary": self.generate_summary(),
        }

    def generate_summary(self) -> Dict:
        """Generate executive summary of analysis"""
        return {
            "total_speakers": len(self.speakers),
            "total_segments": len(self.transcript),
            "total_words": sum(len(seg.words) for seg in self.transcript),
            "critical_discrepancies": len(
                [d for d in self.discrepancies if d.severity == "critical"]
            ),
            "total_discrepancies": len(self.discrepancies),
            "entities_found": {k: len(v) for k, v in self.entities.items()},
            "video_duration_formatted": str(timedelta(seconds=int(self.duration))),
        }


class BWCForensicAnalyzer:
    """
    Court-Defensible BWC Analysis System

    Provides comprehensive forensic analysis of body-worn camera footage
    with features designed for civil rights litigation and court admissibility.
    """

    def __init__(
        self,
        whisper_model_size: str = "base",
        hf_token: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize BWC analyzer with AI models

        Args:
            whisper_model_size: Whisper model size (tiny, base, small, medium, large)
            hf_token: Hugging Face token for pyannote.audio
            device: Device to use (cuda, cpu, mps)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing BWC Analyzer on device: {self.device}")

        # Load Whisper for transcription
        logger.info(f"Loading Whisper model: {whisper_model_size}")
        self.whisper_model = whisper.load_model(whisper_model_size, device=self.device)

        # Load pyannote for speaker diarization
        self.hf_token = hf_token or os.getenv("HUGGINGFACE_TOKEN")
        self.diarization_pipeline = None
        if self.hf_token:
            try:
                logger.info("Loading pyannote speaker diarization pipeline")
                self.diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1", use_auth_token=self.hf_token
                )
                if self.device != "cpu":
                    self.diarization_pipeline.to(torch.device(self.device))
            except Exception as e:
                logger.warning(f"Could not load diarization pipeline: {e}")

        # Load spaCy for entity extraction
        logger.info("Loading spaCy NLP model")
        try:
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            logger.warning("spaCy model not found, downloading...")
            os.system("python -m spacy download en_core_web_md")
            self.nlp = spacy.load("en_core_web_md")

        # Load sentence transformer for semantic search
        logger.info("Loading sentence transformer for semantic search")
        self.sentence_model = SentenceTransformer("all-MiniLM-L6-v2")

        logger.info("✅ BWC Forensic Analyzer initialized successfully")

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for chain of custody"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def establish_chain_of_custody(
        self, file_path: str, acquired_by: str, source: str
    ) -> ChainOfCustody:
        """
        Establish chain of custody for evidence file

        Args:
            file_path: Path to evidence file
            acquired_by: Person/entity who acquired the evidence
            source: How evidence was acquired (OPRA, discovery, etc.)

        Returns:
            ChainOfCustody record
        """
        path = Path(file_path)
        stat = path.stat()

        return ChainOfCustody(
            file_path=str(path.absolute()),
            sha256_hash=self.calculate_file_hash(file_path),
            file_size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            acquired_at=datetime.now(),
            acquired_by=acquired_by,
            source=source,
        )

    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from video file using ffmpeg

        Args:
            video_path: Path to video file
            output_path: Path for output audio file (default: same dir, .wav extension)

        Returns:
            Path to extracted audio file
        """
        if output_path is None:
            output_path = str(Path(video_path).with_suffix(".wav"))

        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",  # No video
            "-acodec",
            "pcm_s16le",  # PCM 16-bit
            "-ar",
            "16000",  # 16kHz sample rate (Whisper standard)
            "-ac",
            "1",  # Mono
            "-y",  # Overwrite output
            output_path,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"✅ Audio extracted to: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract audio: {e.stderr.decode()}")
            raise

    def transcribe_audio(
        self, audio_path: str, language: str = "en", word_timestamps: bool = True
    ) -> Dict:
        """
        Transcribe audio using Whisper

        Args:
            audio_path: Path to audio file
            language: Language code (default: English)
            word_timestamps: Include word-level timestamps

        Returns:
            Transcription result with segments and word timestamps
        """
        logger.info(f"Transcribing audio: {audio_path}")
        result = self.whisper_model.transcribe(
            audio_path, language=language, word_timestamps=word_timestamps, verbose=False
        )
        logger.info(f"✅ Transcription complete: {len(result['segments'])} segments")
        return result

    def diarize_speakers(self, audio_path: str) -> Optional[List[Dict]]:
        """
        Identify and separate speakers in audio

        Args:
            audio_path: Path to audio file

        Returns:
            List of speaker segments with timing and speaker IDs
        """
        if not self.diarization_pipeline:
            logger.warning("Speaker diarization not available (missing HF token)")
            return None

        logger.info(f"Performing speaker diarization: {audio_path}")
        diarization = self.diarization_pipeline(audio_path)

        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({"start": turn.start, "end": turn.end, "speaker": speaker})

        logger.info(f"✅ Identified {len(set(s['speaker'] for s in segments))} speakers")
        return segments

    def merge_transcription_with_speakers(
        self, transcription: Dict, diarization: Optional[List[Dict]]
    ) -> List[TranscriptSegment]:
        """
        Merge Whisper transcription with pyannote speaker diarization

        Args:
            transcription: Whisper transcription result
            diarization: pyannote diarization segments

        Returns:
            List of transcript segments with speaker attribution
        """
        segments = []

        for seg in transcription["segments"]:
            # Find speaker for this segment
            speaker = None
            if diarization:
                seg_mid = (seg["start"] + seg["end"]) / 2
                for d in diarization:
                    if d["start"] <= seg_mid <= d["end"]:
                        speaker = d["speaker"]
                        break

            # Extract words if available
            words = []
            if "words" in seg:
                words = [
                    {
                        "word": w.get("word", ""),
                        "start": w.get("start", 0),
                        "end": w.get("end", 0),
                        "probability": w.get("probability", 1.0),
                    }
                    for w in seg["words"]
                ]

            segments.append(
                TranscriptSegment(
                    start_time=seg["start"],
                    end_time=seg["end"],
                    text=seg["text"].strip(),
                    speaker=speaker,
                    confidence=seg.get("avg_logprob", 1.0),
                    words=words,
                )
            )

        return segments

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text using spaCy

        Args:
            text: Text to analyze

        Returns:
            Dictionary of entity types to entity values
        """
        doc = self.nlp(text)
        entities = {}

        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            if ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)

        return entities

    def label_speakers(
        self, segments: List[TranscriptSegment], known_officers: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Attempt to label speakers based on context and known information

        Args:
            segments: Transcript segments with speaker IDs
            known_officers: List of known officer names

        Returns:
            Mapping of speaker IDs to labels
        """
        speaker_labels = {}
        all_text = " ".join(seg.text for seg in segments)
        entities = self.extract_entities(all_text)

        # Get all unique speakers
        speakers = set(seg.speaker for seg in segments if seg.speaker)

        # Simple heuristic: match speaker to names mentioned near their segments
        for speaker in speakers:
            speaker_text = " ".join(seg.text for seg in segments if seg.speaker == speaker)

            # Check for officer indicators
            if any(
                word in speaker_text.lower() for word in ["officer", "badge", "police", "dispatch"]
            ):
                speaker_labels[speaker] = "Officer (unidentified)"

                # Try to match to known officer
                if known_officers:
                    for officer in known_officers:
                        if officer.lower() in speaker_text.lower():
                            speaker_labels[speaker] = f"Officer {officer}"
                            break
            else:
                speaker_labels[speaker] = "Civilian (unidentified)"

        return speaker_labels

    def detect_discrepancies(
        self,
        transcript: List[TranscriptSegment],
        cad_log: Optional[Dict] = None,
        police_report: Optional[str] = None,
    ) -> List[DiscrepancyReport]:
        """
        Detect discrepancies between BWC footage and other evidence

        Args:
            transcript: BWC transcript segments
            cad_log: CAD log data (timestamps, events, officers)
            police_report: Text of police report

        Returns:
            List of identified discrepancies
        """
        discrepancies = []

        # Extract all entities from BWC
        bwc_text = " ".join(seg.text for seg in transcript)
        bwc_entities = self.extract_entities(bwc_text)

        # Compare with police report if provided
        if police_report:
            report_entities = self.extract_entities(police_report)

            # Check for missing key entities
            for entity_type in ["PERSON", "TIME", "DATE"]:
                bwc_set = set(bwc_entities.get(entity_type, []))
                report_set = set(report_entities.get(entity_type, []))

                missing_from_report = bwc_set - report_set
                missing_from_bwc = report_set - bwc_set

                if missing_from_report:
                    discrepancies.append(
                        DiscrepancyReport(
                            discrepancy_type="statement",
                            severity="major",
                            bwc_evidence=f"{entity_type}: {', '.join(missing_from_report)}",
                            conflicting_evidence=f"Not mentioned in police report",
                            conflicting_source="Police Report",
                            description=f"{entity_type} mentioned in BWC but not in police report",
                            legal_significance="Potential Brady material - exculpatory evidence omitted from official report",
                        )
                    )

        # Check CAD log timestamps if provided
        if cad_log and "events" in cad_log:
            for event in cad_log["events"]:
                # Look for mentions of this event in BWC
                event_type = event.get("type", "")
                event_time = event.get("timestamp", 0)

                # Find closest BWC segment
                closest_seg = min(
                    transcript, key=lambda s: abs((s.start_time + s.end_time) / 2 - event_time)
                )

                time_diff = abs((closest_seg.start_time + closest_seg.end_time) / 2 - event_time)

                # If time difference > 60 seconds, flag as discrepancy
                if time_diff > 60:
                    discrepancies.append(
                        DiscrepancyReport(
                            discrepancy_type="timing",
                            severity="critical" if time_diff > 300 else "major",
                            bwc_evidence=f"Event at BWC timestamp {closest_seg.start_time:.1f}s",
                            conflicting_evidence=f"CAD log shows event at {event_time:.1f}s",
                            conflicting_source="CAD Log",
                            timestamp=event_time,
                            description=f"{time_diff:.1f}s discrepancy in {event_type} timing",
                            legal_significance="Timeline discrepancy may indicate evidence tampering or clock synchronization issues",
                        )
                    )

        return discrepancies

    def analyze_bwc_file(
        self,
        video_path: str,
        acquired_by: str,
        source: str,
        case_number: Optional[str] = None,
        evidence_number: Optional[str] = None,
        known_officers: Optional[List[str]] = None,
        cad_log: Optional[Dict] = None,
        police_report: Optional[str] = None,
    ) -> BWCAnalysisReport:
        """
        Perform comprehensive forensic analysis of BWC file

        Args:
            video_path: Path to BWC video file
            acquired_by: Person who acquired evidence
            source: Source of evidence (OPRA, discovery, etc.)
            case_number: Case docket number
            evidence_number: Evidence tracking number
            known_officers: List of known officer names
            cad_log: CAD log data for cross-referencing
            police_report: Police report text for comparison

        Returns:
            Comprehensive analysis report
        """
        logger.info(f"🔍 Starting BWC forensic analysis: {video_path}")

        # Establish chain of custody
        chain = self.establish_chain_of_custody(video_path, acquired_by, source)
        logger.info(f"✅ Chain of custody established: SHA-256 {chain.sha256_hash[:16]}...")

        # Extract audio from video
        audio_path = self.extract_audio(video_path)

        # Get video metadata
        duration = self.get_video_duration(video_path)
        metadata = self.extract_metadata(video_path)

        # Transcribe audio
        transcription = self.transcribe_audio(audio_path)

        # Perform speaker diarization
        diarization = self.diarize_speakers(audio_path)

        # Merge transcription with speaker identification
        transcript = self.merge_transcription_with_speakers(transcription, diarization)

        # Label speakers
        speaker_labels = self.label_speakers(transcript, known_officers)

        # Apply speaker labels to segments
        for seg in transcript:
            if seg.speaker and seg.speaker in speaker_labels:
                seg.speaker_label = speaker_labels[seg.speaker]

        # Extract entities from full transcript
        full_text = " ".join(seg.text for seg in transcript)
        entities = self.extract_entities(full_text)

        # Detect discrepancies with other evidence
        discrepancies = self.detect_discrepancies(transcript, cad_log, police_report)

        # Create analysis report
        report = BWCAnalysisReport(
            file_name=os.path.basename(video_path),
            file_hash=chain.sha256_hash,
            analysis_date=datetime.now(),
            duration=duration,
            chain_of_custody=chain,
            transcript=transcript,
            speakers=speaker_labels,
            metadata=metadata,
            entities=entities,
            discrepancies=discrepancies,
            case_number=case_number,
            evidence_number=evidence_number,
        )

        logger.info(
            f"✅ Analysis complete: {len(transcript)} segments, {len(speaker_labels)} speakers"
        )
        logger.info(f"⚠️  Found {len(discrepancies)} discrepancies")

        return report

    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds using ffprobe"""
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            logger.warning("Could not determine video duration")
            return 0.0

    def extract_metadata(self, video_path: str) -> Dict:
        """Extract video metadata using ffprobe"""
        cmd = ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", video_path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            logger.warning("Could not extract video metadata")
            return {}

    def export_report(
        self, report: BWCAnalysisReport, output_dir: str, formats: List[str] = ["json", "txt", "md"]
    ) -> List[str]:
        """
        Export analysis report in multiple formats

        Args:
            report: Analysis report to export
            output_dir: Directory for output files
            formats: List of formats (json, txt, md, html)

        Returns:
            List of created file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        base_name = (
            f"BWC_Analysis_{report.file_hash[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        created_files = []

        # JSON format (machine-readable)
        if "json" in formats:
            json_path = output_path / f"{base_name}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
            created_files.append(str(json_path))
            logger.info(f"✅ JSON report: {json_path}")

        # Text format (simple review)
        if "txt" in formats:
            txt_path = output_path / f"{base_name}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self._generate_text_report(report))
            created_files.append(str(txt_path))
            logger.info(f"✅ Text report: {txt_path}")

        # Markdown format (documentation)
        if "md" in formats:
            md_path = output_path / f"{base_name}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(self._generate_markdown_report(report))
            created_files.append(str(md_path))
            logger.info(f"✅ Markdown report: {md_path}")

        return created_files

    def _generate_text_report(self, report: BWCAnalysisReport) -> str:
        """Generate plain text report"""
        lines = [
            "=" * 80,
            "BODY-WORN CAMERA FORENSIC ANALYSIS REPORT",
            "=" * 80,
            "",
            f"File: {report.file_name}",
            f"SHA-256 Hash: {report.file_hash}",
            f"Analysis Date: {report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {timedelta(seconds=int(report.duration))}",
            "",
            f"Case Number: {report.case_number or 'N/A'}",
            f"Evidence Number: {report.evidence_number or 'N/A'}",
            "",
            "-" * 80,
            "CHAIN OF CUSTODY",
            "-" * 80,
            f"Source: {report.chain_of_custody.source}",
            f"Acquired By: {report.chain_of_custody.acquired_by}",
            f"Acquired At: {report.chain_of_custody.acquired_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"File Size: {report.chain_of_custody.file_size:,} bytes",
            f"Verification: {report.chain_of_custody.verification_method}",
            "",
            "-" * 80,
            "TRANSCRIPT",
            "-" * 80,
            "",
        ]

        for seg in report.transcript:
            speaker_label = seg.speaker_label or seg.speaker or "UNKNOWN"
            timestamp = f"[{seg.start_time:.1f}s - {seg.end_time:.1f}s]"
            lines.append(f"{timestamp} {speaker_label}: {seg.text}")

        lines.extend(["", "-" * 80, "ENTITIES EXTRACTED", "-" * 80, ""])

        for entity_type, values in report.entities.items():
            lines.append(f"{entity_type}: {', '.join(values)}")

        if report.discrepancies:
            lines.extend(["", "-" * 80, "DISCREPANCIES DETECTED", "-" * 80, ""])

            for i, disc in enumerate(report.discrepancies, 1):
                lines.extend(
                    [
                        f"{i}. [{disc.severity.upper()}] {disc.discrepancy_type}",
                        f"   BWC Evidence: {disc.bwc_evidence}",
                        f"   Conflicting: {disc.conflicting_evidence}",
                        f"   Source: {disc.conflicting_source}",
                        f"   Legal Significance: {disc.legal_significance}",
                        "",
                    ]
                )

        summary = report.generate_summary()
        lines.extend(
            [
                "",
                "-" * 80,
                "ANALYSIS SUMMARY",
                "-" * 80,
                f"Total Speakers: {summary['total_speakers']}",
                f"Total Segments: {summary['total_segments']}",
                f"Total Words: {summary['total_words']}",
                f"Critical Discrepancies: {summary['critical_discrepancies']}",
                f"Total Discrepancies: {summary['total_discrepancies']}",
                "",
                "=" * 80,
            ]
        )

        return "\n".join(lines)

    def _generate_markdown_report(self, report: BWCAnalysisReport) -> str:
        """Generate Markdown report"""
        lines = [
            "# Body-Worn Camera Forensic Analysis Report",
            "",
            f"**File:** `{report.file_name}`  ",
            f"**SHA-256 Hash:** `{report.file_hash}`  ",
            f"**Analysis Date:** {report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Duration:** {timedelta(seconds=int(report.duration))}  ",
            "",
            f"**Case Number:** {report.case_number or 'N/A'}  ",
            f"**Evidence Number:** {report.evidence_number or 'N/A'}  ",
            "",
            "---",
            "",
            "## Chain of Custody",
            "",
            f"- **Source:** {report.chain_of_custody.source}",
            f"- **Acquired By:** {report.chain_of_custody.acquired_by}",
            f"- **Acquired At:** {report.chain_of_custody.acquired_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **File Size:** {report.chain_of_custody.file_size:,} bytes",
            f"- **Verification Method:** {report.chain_of_custody.verification_method}",
            "",
            "---",
            "",
            "## Transcript",
            "",
            "| Time | Speaker | Text |",
            "|------|---------|------|",
        ]

        for seg in report.transcript:
            speaker_label = seg.speaker_label or seg.speaker or "UNKNOWN"
            timestamp = f"{seg.start_time:.1f}s"
            # Escape pipe characters in text
            text = seg.text.replace("|", "\\|")
            lines.append(f"| {timestamp} | {speaker_label} | {text} |")

        lines.extend(["", "---", "", "## Entities Extracted", ""])

        for entity_type, values in report.entities.items():
            lines.append(f"**{entity_type}:** {', '.join(values)}")

        if report.discrepancies:
            lines.extend(["", "---", "", "## Discrepancies Detected", ""])

            for i, disc in enumerate(report.discrepancies, 1):
                lines.extend(
                    [
                        f"### {i}. [{disc.severity.upper()}] {disc.discrepancy_type}",
                        "",
                        f"- **BWC Evidence:** {disc.bwc_evidence}",
                        f"- **Conflicting Evidence:** {disc.conflicting_evidence}",
                        f"- **Source:** {disc.conflicting_source}",
                        f"- **Legal Significance:** {disc.legal_significance}",
                        "",
                    ]
                )

        summary = report.generate_summary()
        lines.extend(
            [
                "---",
                "",
                "## Analysis Summary",
                "",
                f"- **Total Speakers:** {summary['total_speakers']}",
                f"- **Total Segments:** {summary['total_segments']}",
                f"- **Total Words:** {summary['total_words']}",
                f"- **Critical Discrepancies:** {summary['critical_discrepancies']}",
                f"- **Total Discrepancies:** {summary['total_discrepancies']}",
                "",
                "---",
                "",
                "*Generated by Evident Legal Tech Platform - Court-Defensible eDiscovery*",
            ]
        )

        return "\n".join(lines)


# Command-line interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BWC Forensic Analysis Tool")
    parser.add_argument("video_path", help="Path to BWC video file")
    parser.add_argument("--acquired-by", required=True, help="Person who acquired evidence")
    parser.add_argument("--source", required=True, help="Evidence source (OPRA, discovery, etc.)")
    parser.add_argument("--case-number", help="Case docket number")
    parser.add_argument("--evidence-number", help="Evidence tracking number")
    parser.add_argument("--output-dir", default="./bwc_analysis", help="Output directory")
    parser.add_argument(
        "--whisper-model", default="base", choices=["tiny", "base", "small", "medium", "large"]
    )
    parser.add_argument("--hf-token", help="Hugging Face token for speaker diarization")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = BWCForensicAnalyzer(whisper_model_size=args.whisper_model, hf_token=args.hf_token)

    # Analyze BWC file
    report = analyzer.analyze_bwc_file(
        video_path=args.video_path,
        acquired_by=args.acquired_by,
        source=args.source,
        case_number=args.case_number,
        evidence_number=args.evidence_number,
    )

    # Export reports
    files = analyzer.export_report(report, args.output_dir)

    print("\n✅ Analysis complete!")
    print(f"📊 Reports generated:")
    for f in files:
        print(f"   - {f}")


