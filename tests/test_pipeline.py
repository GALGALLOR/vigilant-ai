from workers.pipeline import (
    ALERT_B_THRESHOLD,
    compute_alert_score,
    extract_caption_threats,
    find_active_windows,
    infer_domain,
    label_from_signals,
    make_subclips,
    make_video_chunks,
)


def test_make_video_chunks():
    assert make_video_chunks(610, 300) == [(0.0, 300.0), (300.0, 600.0), (600.0, 610)]


def test_find_active_windows_merge_and_filter():
    series = [
        (0.0, 0.01),
        (1.0, 0.06),
        (2.0, 0.07),
        (3.0, 0.01),
        (6.0, 0.08),
        (7.0, 0.08),
        (8.5, 0.01),
    ]
    windows = find_active_windows(series, motion_threshold=0.05, min_window_secs=1.5, merge_gap_secs=5.0)
    assert windows == [(1.0, 8.5)]


def test_make_subclips_with_overlap():
    assert make_subclips(0, 21, duration=10, overlap=2) == [(0, 10), (8, 18), (16, 21)]


def test_extract_caption_threats_human_dog_antitheft():
    tags = extract_caption_threats(
        "Two people fight while dogs fighting nearby and theft stealing happens with a window smash"
    )
    assert "physical_altercation" in tags
    assert "dog_fight" in tags
    assert "theft_suspected" in tags
    assert "vehicle_break_in" in tags


def test_label_from_signals_human():
    signals = {"contact_score": 0.8, "peak_motion": 0.9, "after_hours": 0, "dog_count": 0}
    label, confidence, _ = label_from_signals(signals, ["physical_altercation"])
    assert label == "physical_altercation"
    assert confidence > 0.7


def test_label_from_signals_dog():
    signals = {"contact_score": 0.75, "peak_motion": 0.6, "dog_count": 2, "after_hours": 0}
    label, confidence, _ = label_from_signals(signals, ["dog_fight", "dog_aggression"])
    assert label == "dog_fight"
    assert confidence > 0.7


def test_label_from_signals_antitheft():
    signals = {"contact_score": 0.2, "peak_motion": 0.2, "dog_count": 0, "after_hours": 1}
    label, confidence, _ = label_from_signals(signals, ["package_theft", "snatch_and_run"])
    assert label in {"package_theft", "snatch_and_run"}
    assert confidence > 0.7


def test_infer_domain_prefers_dog_with_dog_count():
    domain = infer_domain({"dog_count": 1}, ["theft_suspected"])
    assert domain == "dog_safety"


def test_compute_alert_score_safe_cap():
    score, stage, _ = compute_alert_score(
        "handshake",
        {"contact_score": 0.9, "peak_motion": 0.9, "people_count": 3, "vehicle_count": 0, "dog_count": 0, "after_hours": 0},
        ["handshake"],
    )
    assert score < ALERT_B_THRESHOLD
    assert stage in {"A", "none"}


def test_compute_alert_score_critical_antitheft():
    score, stage, _ = compute_alert_score(
        "vehicle_break_in",
        {"contact_score": 0.2, "peak_motion": 0.3, "people_count": 1, "vehicle_count": 1, "dog_count": 0, "after_hours": 1},
        ["vehicle_break_in"],
    )
    assert score >= 0.7
    assert stage == "C"
