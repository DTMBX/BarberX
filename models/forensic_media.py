"""
Forensic Audio and Video Processing Models
Military-grade forensic analysis for authenticity, speaker identification,
and court-admissible metadata preservation
"""

from datetime import datetime, timedelta
from enum import Enum
from auth.models import db, User


class MediaType(Enum):
    """Types of media that can be forensically analyzed"""
    AUDIO = "audio"
    VIDEO = "video"
    TRANSCRIPT = "transcript"
    MULTIMEDIA = "multimedia"


class ForensicStatus(Enum):
    """Forensic analysis status"""
    PENDING = "pending"
    PROCESSING = "processing"
    METADATA_EXTRACTED = "metadata_extracted"
    AUTHENTICITY_ANALYZED = "authenticity_analyzed"
    COMPLETE = "complete"
    FAILED = "failed"


class AuthenticityLevel(Enum):
    """Forensic verdict on authenticity"""
    AUTHENTIC = "authentic"
    LIKELY_AUTHENTIC = "likely_authentic"
    QUESTIONABLE = "questionable"
    LIKELY_EDITED = "likely_edited"
    EDITED = "edited"
    UNKNOWN = "unknown"


class ForensicAudioMetadata(db.Model):
    """
    Comprehensive forensic analysis of audio recordings
    Stores military-grade authenticity verification
    """
    __tablename__ = 'forensic_audio_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False, unique=True, index=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False, index=True)
    
    # File Information
    file_path = db.Column(db.String(500), nullable=False)
    file_size_bytes = db.Column(db.Integer)
    file_hash_sha256 = db.Column(db.String(64), unique=True)  # Cryptographic hash
    file_format = db.Column(db.String(20))  # mp3, wav, m4a, ogg
    codec = db.Column(db.String(50))  # AAC, MP3, PCM, FLAC
    
    # Basic Audio Properties
    duration_seconds = db.Column(db.Float)
    sample_rate_hz = db.Column(db.Integer)  # 16000, 44100, 48000, etc.
    bit_depth = db.Column(db.Integer)  # 16, 24, 32 bit
    channels = db.Column(db.Integer)  # mono, stereo, 5.1, etc.
    bitrate_kbps = db.Column(db.Integer)
    
    # Recording Metadata
    recording_date = db.Column(db.DateTime)  # When recorded
    recording_location = db.Column(db.String(300))  # Physical location
    recording_device = db.Column(db.String(200))  # Device used
    device_make_model = db.Column(db.String(200))
    microphone_information = db.Column(db.String(300))
    
    # Forensic Analysis
    analysis_status = db.Column(db.String(50), default="pending")  # ForensicStatus
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_complete = db.Column(db.Boolean, default=False)
    
    # Authenticity Assessment
    authenticity_verdict = db.Column(db.String(50), default="unknown")  # AuthenticityLevel
    authenticity_confidence = db.Column(db.Float)  # 0-1 confidence in verdict
    
    # Splicing & Editing Detection
    splices_detected = db.Column(db.Integer, default=0)  # Number of detected splices
    edit_markers = db.Column(db.Text)  # JSON: {timestamp, type, confidence}
    unnatural_transitions = db.Column(db.Integer, default=0)  # Frequency changes
    
    # Frequency Analysis
    frequency_anomalies = db.Column(db.Text)  # JSON: detected anomalies
    noise_floor = db.Column(db.Float)  # dB level
    signal_noise_ratio = db.Column(db.Float)  # dB SNR
    compression_detected = db.Column(db.Boolean, default=False)
    compression_type = db.Column(db.String(50))  # MP3, AAC, OPUS, etc.
    
    # Enhancement/Processing Detection
    voice_modification = db.Column(db.Boolean, default=False)  # Speed, pitch altered
    pitch_shift_detected = db.Column(db.Boolean, default=False)
    time_stretch_detected = db.Column(db.Boolean, default=False)
    noise_reduction_applied = db.Column(db.Boolean, default=False)
    equalization_applied = db.Column(db.Boolean, default=False)
    
    # Speaker Analysis
    num_speakers_detected = db.Column(db.Integer)
    speaker_count_confidence = db.Column(db.Float)
    speaker_segments = db.Column(db.Text)  # JSON: time ranges for each speaker
    
    # Audio Quality Metrics
    loudness_lufs = db.Column(db.Float)  # Perceived loudness (LUFS)
    dynamic_range = db.Column(db.Float)  # dB
    clipping_detected = db.Column(db.Boolean, default=False)
    peak_level = db.Column(db.Float)  # dBFS
    
    # Metadata Artifacts
    metadata_intact = db.Column(db.Boolean, default=True)
    metadata_inconsistencies = db.Column(db.Text)  # JSON: found inconsistencies
    
    # Chain of Custody
    custodian = db.Column(db.String(200))
    acquisition_date = db.Column(db.DateTime)
    acquisition_method = db.Column(db.String(100))  # original, dump, recovery
    forensic_examiner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    examiner_certification = db.Column(db.String(100))  # CFCA, CFCE, etc.
    
    # Court Admissibility
    court_admissible = db.Column(db.Boolean, default=False)
    frcp_compliance = db.Column(db.Boolean, default=False)
    fte_rule_901_compliance = db.Column(db.Boolean, default=False)  # Authentication
    daubert_challenge_risk = db.Column(db.Float)  # 0-1 risk of Daubert challenge
    
    # Detailed Report
    forensic_report = db.Column(db.Text)  # Full forensic analysis report
    technical_specifications = db.Column(db.Text)  # Detailed tech specs
    testing_methodology = db.Column(db.Text)  # How analysis was performed
    industry_standards_used = db.Column(db.Text)  # NIST, FBI, ASCLD/LAB
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    examiner = db.relationship('User', foreign_keys=[forensic_examiner_id])
    
    def __repr__(self):
        return f'<ForensicAudioMetadata Evidence:{self.evidence_id}>'


class ForensicVideoMetadata(db.Model):
    """
    Comprehensive forensic analysis of video recordings
    Stores military-grade authenticity verification
    """
    __tablename__ = 'forensic_video_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False, unique=True, index=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False, index=True)
    
    # File Information
    file_path = db.Column(db.String(500), nullable=False)
    file_size_bytes = db.Column(db.Integer)
    file_hash_sha256 = db.Column(db.String(64), unique=True)  # Cryptographic hash
    file_format = db.Column(db.String(20))  # mp4, mov, avi, mkv
    container_format = db.Column(db.String(50))  # MPEG, QuickTime, AVI
    
    # Video Properties
    duration_seconds = db.Column(db.Float)
    width_pixels = db.Column(db.Integer)
    height_pixels = db.Column(db.Integer)
    frame_rate = db.Column(db.Float)  # fps
    total_frames = db.Column(db.Integer)
    
    # Video Codec
    video_codec = db.Column(db.String(50))  # H.264, H.265, PRORES, DNxHD
    bitrate_mbps = db.Column(db.Float)
    profile = db.Column(db.String(100))  # baseline, main, high
    
    # Audio Track
    audio_codec = db.Column(db.String(50))
    audio_channels = db.Column(db.Integer)
    audio_sample_rate = db.Column(db.Integer)
    
    # Recording Metadata
    recording_date = db.Column(db.DateTime)
    recording_location = db.Column(db.String(300))
    recording_device = db.Column(db.String(200))
    device_make_model = db.Column(db.String(200))
    lens_information = db.Column(db.String(200))
    
    # Forensic Analysis
    analysis_status = db.Column(db.String(50), default="pending")
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_complete = db.Column(db.Boolean, default=False)
    
    # Authenticity Assessment
    authenticity_verdict = db.Column(db.String(50), default="unknown")
    authenticity_confidence = db.Column(db.Float)  # 0-1
    
    # Edit/Splice Detection
    edits_detected = db.Column(db.Integer, default=0)
    edit_markers = db.Column(db.Text)  # JSON: frame numbers and types
    frame_duplication = db.Column(db.Boolean, default=False)  # Repeated frames
    duplicated_frame_sequences = db.Column(db.Text)  # JSON: ranges
    
    # Temporal Anomalies
    temporal_inconsistencies = db.Column(db.Integer, default=0)
    frame_rate_changes = db.Column(db.Text)  # JSON
    timestamp_discontinuities = db.Column(db.Boolean, default=False)
    timecode_issues = db.Column(db.Text)  # JSON
    
    # Compression & Reencoding
    reencoding_detected = db.Column(db.Boolean, default=False)
    generation_loss = db.Column(db.Float)  # Estimate of quality loss
    compression_artifacts = db.Column(db.Text)  # JSON
    
    # Metadata Integrity
    exif_data_present = db.Column(db.Boolean, default=False)
    exif_data = db.Column(db.Text)  # JSON: extracted EXIF
    exif_data_consistent = db.Column(db.Boolean)
    geolocation_data = db.Column(db.String(300))  # lat, lon if available
    
    # Thumbnail/Preview Frame Analysis
    key_frames = db.Column(db.Integer)  # Number of key frames
    key_frame_consistency = db.Column(db.Boolean)
    
    # Frame Analysis
    total_frames_analyzed = db.Column(db.Integer)
    anomalous_frames = db.Column(db.Integer)
    transition_anomalies = db.Column(db.Integer)
    color_space = db.Column(db.String(20))  # YUV, RGB, etc.
    color_consistency = db.Column(db.Boolean)
    
    # Motion Analysis
    motion_estimation_error = db.Column(db.Float)  # Unnatural motion detected
    optical_flow_anomalies = db.Column(db.Integer)
    unnatural_movement = db.Column(db.Boolean, default=False)
    
    # Deepfake Detection
    deepfake_score = db.Column(db.Float)  # 0-1 likelihood of deepfake
    face_detection_confidence = db.Column(db.Float)
    face_morphing_detected = db.Column(db.Boolean, default=False)
    synthetic_faces = db.Column(db.Integer, default=0)
    
    # Audio Sync
    audio_video_synchronized = db.Column(db.Boolean, default=True)
    sync_offset_frames = db.Column(db.Integer, default=0)  # Frame desynchronization
    
    # Chain of Custody
    custodian = db.Column(db.String(200))
    acquisition_date = db.Column(db.DateTime)
    acquisition_method = db.Column(db.String(100))
    forensic_examiner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    examiner_certification = db.Column(db.String(100))
    
    # Court Admissibility
    court_admissible = db.Column(db.Boolean, default=False)
    frcp_compliance = db.Column(db.Boolean, default=False)
    fte_rule_901_compliance = db.Column(db.Boolean, default=False)
    daubert_challenge_risk = db.Column(db.Float)  # 0-1
    
    # Detailed Report
    forensic_report = db.Column(db.Text)
    technical_specifications = db.Column(db.Text)
    testing_methodology = db.Column(db.Text)
    industry_standards_used = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    examiner = db.relationship('User', foreign_keys=[forensic_examiner_id])
    
    def __repr__(self):
        return f'<ForensicVideoMetadata Evidence:{self.evidence_id}>'


class SpeakerIdentification(db.Model):
    """Speaker identification and diarization results"""
    __tablename__ = 'speaker_identification'
    
    id = db.Column(db.Integer, primary_key=True)
    audio_metadata_id = db.Column(db.Integer, db.ForeignKey('forensic_audio_metadata.id'), nullable=False)
    
    # Speaker Info
    speaker_label = db.Column(db.String(100), nullable=False)  # Speaker 1, Speaker 2, etc.
    speaker_name = db.Column(db.String(200))  # Identified name if known
    speaker_role = db.Column(db.String(100))  # Witness, defendant, attorney, etc.
    
    # Voice Characteristics
    fundamental_frequency = db.Column(db.Float)  # Hz
    voice_quality = db.Column(db.String(100))
    accent_detected = db.Column(db.String(100))
    speech_rate_wpm = db.Column(db.Float)  # Words per minute
    
    # Identification Accuracy
    speaker_confidence = db.Column(db.Float)  # 0-1
    voice_biometric_score = db.Column(db.Float)  # Similarity to known voice sample
    
    # Segments
    total_speaking_time_seconds = db.Column(db.Float)
    segment_count = db.Column(db.Integer)
    segments = db.Column(db.Text)  # JSON: [{start_time, end_time, duration}]
    
    # Voice Print
    voice_print_created = db.Column(db.Boolean, default=False)
    voice_print_hash = db.Column(db.String(64))  # Voice template hash
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SpeakerIdentification {self.speaker_label}>'


class AudioTranscription(db.Model):
    """Court-grade transcription with confidence scoring"""
    __tablename__ = 'audio_transcription'
    
    id = db.Column(db.Integer, primary_key=True)
    audio_metadata_id = db.Column(db.Integer, db.ForeignKey('forensic_audio_metadata.id'), nullable=False)
    
    # Transcription Details
    transcription_text = db.Column(db.Text, nullable=False)
    transcription_model = db.Column(db.String(100))  # Whisper-large v3, etc.
    model_version = db.Column(db.String(50))
    
    # Accuracy Metrics
    word_error_rate = db.Column(db.Float)  # 0-1 WER
    character_error_rate = db.Column(db.Float)  # 0-1 CER
    confidence_overall = db.Column(db.Float)  # 0-1 overall confidence
    
    # Segment-Level Confidence
    segments = db.Column(db.Text)  # JSON: [{text, start, end, confidence, speaker}]
    
    # Difficult Passages
    low_confidence_segments = db.Column(db.Integer)  # Count of segments < 80% confidence
    challenging_audio_noted = db.Column(db.Text)  # JSON: background noise, accents, etc.
    
    # Speaker Attribution
    speaker_attribution_confidence = db.Column(db.Float)  # How sure about who said what
    
    # Technical Corrections
    homophone_notes = db.Column(db.Text)  # JSON: corrected homophones
    proper_nouns_identified = db.Column(db.Text)  # JSON: names, places, organizations
    
    # Edit Summary
    human_corrected = db.Column(db.Boolean, default=False)
    corrected_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    corrected_date = db.Column(db.DateTime)
    correction_notes = db.Column(db.Text)
    
    # Court Admissibility
    court_certified = db.Column(db.Boolean, default=False)
    certification_date = db.Column(db.DateTime)
    certified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    corrected_by = db.relationship('User', foreign_keys=[corrected_by_id])
    certified_by = db.relationship('User', foreign_keys=[certified_by_id])
    
    def __repr__(self):
        return f'<AudioTranscription Audio:{self.audio_metadata_id}>'


class ForensicChainOfCustody(db.Model):
    """Cryptographic chain of custody for media evidence"""
    __tablename__ = 'forensic_chain_of_custody'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False, unique=True)
    
    # Original Evidence
    original_file_hash = db.Column(db.String(64), nullable=False)  # SHA-256
    original_hash_algorithm = db.Column(db.String(20), default="SHA-256")
    original_timestamp = db.Column(db.DateTime, nullable=False)
    
    # Custody Chain
    chain_entries = db.Column(db.Text, nullable=False)  # JSON: [{date, custodian, location, action}]
    
    # Access Logs
    access_logs = db.Column(db.Text)  # JSON: [{timestamp, user, action, result_hash}]
    
    # Integrity Verification
    currently_verified = db.Column(db.Boolean, default=False)
    last_verified_date = db.Column(db.DateTime)
    last_verified_hash = db.Column(db.String(64))
    
    # Tamper Detection
    integrity_intact = db.Column(db.Boolean, default=True)
    tampering_detected = db.Column(db.Boolean, default=False)
    tampering_details = db.Column(db.Text)
    
    # Digital Signature
    signed = db.Column(db.Boolean, default=False)
    signature = db.Column(db.Text)  # Cryptographic signature
    signing_certificate = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ForensicChainOfCustody Evidence:{self.evidence_id}>'


class MediaForensicReport(db.Model):
    """Professional forensic examination report"""
    __tablename__ = 'media_forensic_report'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False, unique=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Report Details
    examiner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    examiner_name = db.Column(db.String(200))
    examiner_qualifications = db.Column(db.Text)  # Expertise, certifications
    
    # Report Content
    executive_summary = db.Column(db.Text)  # High-level findings
    detailed_findings = db.Column(db.Text)  # Technical analysis
    methodology = db.Column(db.Text)  # How testing was done
    
    # Standards & Compliance
    industry_standards_applied = db.Column(db.Text)  # NIST, FBI, ASCLD/LAB
    professional_guidelines = db.Column(db.Text)  # AAFS standards
    
    # Conclusions
    conclusions = db.Column(db.Text)  # Final expert opinions
    opinions_to_reasonable_certainty = db.Column(db.Text)  # Expert opinions
    
    # Limitations
    limitations = db.Column(db.Text)  # What couldn't be determined
    disclaimers = db.Column(db.Text)  # Professional disclaimers
    
    # Court Readiness
    court_ready = db.Column(db.Boolean, default=False)
    suitable_for_expert_testimony = db.Column(db.Boolean, default=False)
    daubert_compliance = db.Column(db.Text)  # Daubert factor analysis
    
    # Report Date & Version
    report_date = db.Column(db.DateTime, nullable=False)
    report_version = db.Column(db.Float, default=1.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    examiner = db.relationship('User', foreign_keys=[examiner_id])
    
    def __repr__(self):
        return f'<MediaForensicReport Evidence:{self.evidence_id}>'
