from backend.src.bwc_flags import analyze_transcript_for_flags


def test_flags_detect_profanity_and_phrases():
    transcripts = [
        [
            {"start_time": 0.0, "end_time": 1.0, "text": "What the fuck happened?"},
            {"start_time": 1.0, "end_time": 2.0, "text": "Step out of the vehicle"},
        ],
        [{"start_time": 0.0, "end_time": 1.0, "text": "Officer: put your hands up"}],
    ]

    flags = analyze_transcript_for_flags(transcripts)
    # Expect at least 3 flags (profanity + step out + put your hands)
    assert any(f.rule_id == "profanity" for f in flags)
    assert any(f.rule_id.startswith("proc_") or f.rule_id.startswith("force_") for f in flags)
