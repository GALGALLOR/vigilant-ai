"""
Vigilant-AI — Consolidated Incident Report Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Produces ONE report per video, regardless of how many individual alert clips fired.

Design principle: if someone is assaulted repeatedly for 5 minutes across 30 clips,
the report describes ONE incident with a sustained timeline — not 30 separate incidents.

Report structure:
  - Executive summary (single narrative)
  - Incident classification + severity
  - Estimated parties involved
  - Consolidated timeline (key moments, not every clip)
  - Evidence clips (top alerts only)
  - Analyst recommendations
"""

from __future__ import annotations
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


# ─── Report Generator ────────────────────────────────────────────────────────

def generate_incident_report(
    video_id: str,
    video_name: str,
    events: List[Dict],
    synthesis: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Generate a single consolidated incident report for an entire video.

    Consolidation logic:
      - Groups all Stage B/C alerts as one continuous incident
      - Computes an overall timeline span (first alert → last alert)
      - Passes ONLY the top alerts + summary to Gemini (not every 10s clip)
        → prevents 30 separate sub-reports for a 5-minute assault
    """
    from services.gemini_synthesis import _call_gemini, _fmt_time

    # ── 1. Separate alerts vs normal events ──────────────────────────────────
    alerts = [e for e in events if _get_stage(e) in ("B", "C")]
    alerts.sort(key=lambda e: e.get("start", 0))

    if not alerts and not events:
        return _empty_report(video_id, video_name)

    # If no B/C alerts but events exist, use top events by alert_score
    if not alerts:
        alerts = sorted(events, key=lambda e: _get_score(e), reverse=True)[:5]

    # ── 2. Compute consolidated incident window from ALL events sorted by time ──
    # (NOT from the score-filtered fallback — that gives wrong start/end times)
    all_sorted = sorted(events, key=lambda e: e.get("start", 0))
    incident_start = all_sorted[0].get("start", 0) if all_sorted else 0
    incident_end   = all_sorted[-1].get("end", all_sorted[-1].get("start", 0)) if all_sorted else 0
    duration_s     = max(incident_end - incident_start, 0)

    # ── 3. Pick representative evidence clips (max 8, diverse across timeline) ─
    step = max(1, len(alerts) // 8)
    evidence_clips = alerts[::step][:8]

    # ── 4. Aggregate detection signals ───────────────────────────────────────
    max_people  = max((_get_people(e) for e in alerts), default=0)
    max_contact = max((e.get("detections", {}).get("contact_score",
                        e.get("evidence", {}).get("overlap", 0)) for e in alerts), default=0)
    labels      = list(dict.fromkeys(_get_label(e) for e in alerts if _get_label(e)))
    stage_c_count = sum(1 for e in alerts if _get_stage(e) == "C")

    # ── 5. Build Gemini prompt ────────────────────────────────────────────────
    _api_err = {"api error", "api error.", "[api error]", "api_error"}

    def _safe_caption(e: Dict) -> str:
        cap = e.get("caption", "")
        if cap.strip().lower() in _api_err:
            return f"[visual details unavailable — label={_get_label(e)}, stage={_get_stage(e)}]"
        return cap

    clips_text = "\n".join(
        f"  [{_fmt_time(e.get('start',0))}–{_fmt_time(e.get('end',0))}] "
        f"stage={_get_stage(e)} score={_get_score(e):.2f} | {_safe_caption(e)}"
        for e in evidence_clips
    )

    video_summary_text = synthesis.get("summary", "") if synthesis else ""
    prior_summary = f"\nOVERALL VIDEO ANALYSIS:\n{video_summary_text}\n" if video_summary_text else ""

    prompt = f"""You are a professional security analyst writing a formal incident report.
Video: "{video_name}"
Incident window: {_fmt_time(incident_start)} – {_fmt_time(incident_end)} (duration: {duration_s:.0f}s)
Detected labels: {', '.join(labels[:5]) or 'unclassified'}
Max people in frame: {max_people}
Stage-C (critical) clips: {stage_c_count}
Total alert clips: {len(alerts)}
{prior_summary}
REPRESENTATIVE EVIDENCE CLIPS (sample across the full incident — NOT all clips):
{clips_text}

Write a single consolidated incident report. Do NOT write one section per clip.
Treat this as ONE incident that may have sustained phases.

Respond ONLY with raw JSON (no markdown, no code fences):
{{
  "title": "Brief incident title (e.g., 'Physical Assault — Sustained Attack')",
  "classification": "assault|theft|trespassing|vandalism|suspicious_behavior|medical|other",
  "severity": "critical|high|medium|low",
  "executive_summary": "2–3 paragraph narrative describing the full incident as ONE event. Mention start/end times. Do not reference individual 10-second clips.",
  "incident_window": {{"start": "{_fmt_time(incident_start)}", "end": "{_fmt_time(incident_end)}", "duration_s": {duration_s:.0f}}},
  "parties": {{
    "total_persons": {max_people},
    "perpetrators_estimated": 0,
    "victims_estimated": 0,
    "note": "brief description of parties"
  }},
  "key_moments": [
    {{"time": "M:SS", "description": "What happened at this moment"}}
  ],
  "physical_indicators": {{
    "contact_detected": {"true" if max_contact > 0.3 else "false"},
    "max_contact_score": {max_contact:.2f},
    "sustained": {"true" if duration_s > 60 else "false"}
  }},
  "recommendations": [
    "Immediate action recommendation",
    "Follow-up action",
    "Preventive measure"
  ]
}}"""

    raw = _call_gemini(prompt, max_tokens=1500)
    report_data = _parse_gemini_json(raw)

    # ── 6. Merge generated data with computed facts ───────────────────────────
    report = {
        "report_id":    f"RPT-{video_id.upper()[:8]}-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
        "video_id":     video_id,
        "video_name":   video_name,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_alerts": len(alerts),
        "total_events": len(events),
        **report_data,
        "evidence_clips": [
            {
                "clip_id":    e.get("clip_id"),
                "time_start": _fmt_time(e.get("start", 0)),
                "time_end":   _fmt_time(e.get("end", 0)),
                "stage":      _get_stage(e),
                "score":      round(_get_score(e), 3),
                "caption":    e.get("caption", ""),
            }
            for e in evidence_clips
        ],
    }
    return report


# ─── Plain-text export ───────────────────────────────────────────────────────

def report_to_text(report: Dict) -> str:
    """Render a report dict as a human-readable plain-text document."""
    lines = [
        "=" * 70,
        f"  VIGILANT-AI SECURITY INCIDENT REPORT",
        "=" * 70,
        f"  Report ID   : {report.get('report_id', 'N/A')}",
        f"  Video       : {report.get('video_name', '')}",
        f"  Generated   : {report.get('generated_at', '')}",
        f"  Severity    : {report.get('severity', '').upper()}",
        f"  Class       : {report.get('classification', '').replace('_', ' ').title()}",
        "=" * 70,
        "",
        f"TITLE: {report.get('title', '')}",
        "",
        "─" * 70,
        "EXECUTIVE SUMMARY",
        "─" * 70,
        report.get("executive_summary", ""),
        "",
    ]

    iw = report.get("incident_window", {})
    if iw:
        lines += [
            "─" * 70,
            "INCIDENT WINDOW",
            "─" * 70,
            f"  Start    : {iw.get('start', 'N/A')}",
            f"  End      : {iw.get('end',   'N/A')}",
            f"  Duration : {iw.get('duration_s', 0):.0f}s",
            "",
        ]

    parties = report.get("parties", {})
    if parties:
        lines += [
            "─" * 70,
            "PARTIES INVOLVED",
            "─" * 70,
            f"  Total persons in frame : {parties.get('total_persons', '?')}",
            f"  Perpetrators (est.)    : {parties.get('perpetrators_estimated', '?')}",
            f"  Victims (est.)         : {parties.get('victims_estimated', '?')}",
            f"  Note                   : {parties.get('note', '')}",
            "",
        ]

    km = report.get("key_moments", [])
    if km:
        lines += ["─" * 70, "KEY MOMENTS", "─" * 70]
        for m in km:
            lines.append(f"  {m.get('time','?')}  {m.get('description','')}")
        lines.append("")

    recs = report.get("recommendations", [])
    if recs:
        lines += ["─" * 70, "RECOMMENDATIONS", "─" * 70]
        for i, r in enumerate(recs, 1):
            lines.append(f"  {i}. {r}")
        lines.append("")

    ec = report.get("evidence_clips", [])
    if ec:
        lines += ["─" * 70, f"EVIDENCE CLIPS ({len(ec)} key moments selected from {report.get('total_alerts', '?')} alerts)", "─" * 70]
        for c in ec:
            lines.append(f"  [{c.get('time_start','?')}–{c.get('time_end','?')}] Stage-{c.get('stage','?')} ({c.get('score',0):.2f})  {c.get('caption','')}")
        lines.append("")

    lines += ["=" * 70, "  END OF REPORT — Vigilant AI · HackIllinois 2026", "=" * 70]
    return "\n".join(lines)


# ─── PDF export ──────────────────────────────────────────────────────────────

def report_to_pdf(report: Dict) -> bytes:
    """Render a report dict as a PDF and return raw bytes (requires fpdf2)."""
    try:
        from fpdf import FPDF
    except ImportError:
        raise RuntimeError("fpdf2 is not installed — run: pip install fpdf2")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Header bar ────────────────────────────────────────────────────────────
    pdf.set_fill_color(18, 18, 28)
    pdf.set_text_color(230, 200, 100)      # amber
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 13, "VIGILANT AI - SECURITY INCIDENT REPORT", fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_fill_color(30, 30, 48)
    pdf.set_text_color(160, 160, 190)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(
        0, 6,
        f"Report ID: {report.get('report_id','N/A')}   |   "
        f"Generated: {report.get('generated_at','')[:19].replace('T',' ')}   |   "
        f"Vigilant AI · HackIllinois 2026",
        fill=True, align="C", new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(3)

    # ── Meta row ──────────────────────────────────────────────────────────────
    sev = report.get("severity", "unknown").upper()
    cls_ = report.get("classification", "").replace("_", " ").title()
    pdf.set_text_color(40, 40, 50)
    pdf.set_font("Helvetica", "B", 9)
    meta_text = f"Video: {report.get('video_name','')}   |   Severity: {sev}   |   Classification: {cls_}"
    meta_text = "".join(c if ord(c) < 256 else "?" for c in meta_text)
    pdf.cell(0, 7, meta_text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Section helper ──────────────────────────────────────────────────────────
    def _section(title: str) -> None:
        pdf.set_fill_color(235, 235, 248)
        pdf.set_text_color(40, 40, 90)
        pdf.set_font("Helvetica", "B", 8.5)
        safe_title = "".join(c if ord(c) < 256 else "?" for c in title)
        pdf.cell(0, 6.5, safe_title, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)

    def _body(text: str, size: float = 9) -> None:
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(40, 40, 50)
        # Built-in Helvetica only supports latin-1 (0-255) — replace anything outside
        safe = (text or "").replace("\u2014", "-").replace("\u2013", "-").replace("\u2022", "*")
        safe = "".join(c if ord(c) < 256 else "?" for c in safe)
        pdf.multi_cell(0, 5, safe)
        pdf.ln(1.5)

    # ── Title ─────────────────────────────────────────────────────────────────
    _section("INCIDENT TITLE")
    _body(report.get("title", "Untitled Incident"), size=10)

    # ── Executive Summary ─────────────────────────────────────────────────────
    _section("EXECUTIVE SUMMARY")
    _body(report.get("executive_summary", "No summary available."))

    # ── Incident Window ───────────────────────────────────────────────────────
    iw = report.get("incident_window", {})
    if iw:
        _section("INCIDENT WINDOW")
        _body(
            f"Start: {iw.get('start','N/A')}   |   End: {iw.get('end','N/A')}   |   "
            f"Duration: {iw.get('duration_s', 0):.0f}s"
        )

    # ── Parties ───────────────────────────────────────────────────────────────
    parties = report.get("parties", {})
    if parties:
        _section("PARTIES INVOLVED")
        _body(
            f"Total persons in frame: {parties.get('total_persons','?')}\n"
            f"Perpetrators (estimated): {parties.get('perpetrators_estimated','?')}\n"
            f"Victims (estimated): {parties.get('victims_estimated','?')}\n"
            f"Note: {parties.get('note','')}"
        )

    # ── Key Moments ───────────────────────────────────────────────────────────
    km = report.get("key_moments", [])
    if km:
        _section(f"KEY MOMENTS  ({len(km)})")
        for m in km:
            _body(f"  {m.get('time','?')}   {m.get('description','')}")

    # ── Recommendations ───────────────────────────────────────────────────────
    recs = report.get("recommendations", [])
    if recs:
        _section("RECOMMENDATIONS")
        for i, r in enumerate(recs, 1):
            _body(f"{i}. {r}")

    # ── Evidence Clips ────────────────────────────────────────────────────────
    ec = report.get("evidence_clips", [])
    if ec:
        _section(f"EVIDENCE CLIPS  ({len(ec)} selected from {report.get('total_alerts','?')} alerts)")
        for c in ec:
            cap = c.get("caption", "")
            _body(
                f"[{c.get('time_start','?')} – {c.get('time_end','?')}]  "
                f"Stage-{c.get('stage','?')} ({c.get('score',0):.2f})   {cap}",
                size=8.5,
            )

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 5, "End of Report - Vigilant AI / HackIllinois 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_stage(e: Dict) -> str:
    a = e.get("alert", {})
    if isinstance(a, dict): return a.get("stage", "none")
    return e.get("alert_stage", "none")

def _get_score(e: Dict) -> float:
    a = e.get("alert", {})
    if isinstance(a, dict): return float(a.get("score", 0))
    return float(e.get("alert_score", 0))

def _get_people(e: Dict) -> int:
    d = e.get("detections", {})
    if isinstance(d, dict): return d.get("people_count", 0)
    return e.get("people_count", 0)

def _get_label(e: Dict) -> str:
    ev = e.get("event", {})
    if isinstance(ev, dict): return ev.get("label", "")
    return e.get("event_type", "")

def _parse_gemini_json(raw: str) -> Dict:
    if not raw:
        return {}
    from services.gemini_synthesis import _clean_json_string
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = _clean_json_string(cleaned.strip())
        return json.loads(cleaned)
    except Exception:
        return {"executive_summary": raw[:500], "title": "Incident Report", "severity": "unknown", "classification": "other"}

def _empty_report(video_id: str, video_name: str) -> Dict:
    return {
        "report_id":       f"RPT-{video_id.upper()[:8]}-EMPTY",
        "video_id":        video_id,
        "video_name":      video_name,
        "generated_at":    datetime.utcnow().isoformat() + "Z",
        "title":           "No Incidents Detected",
        "classification":  "normal_activity",
        "severity":        "low",
        "executive_summary": "No alert-level incidents were detected in this video.",
        "total_alerts":    0,
        "total_events":    0,
        "recommendations": ["Continue routine monitoring."],
        "evidence_clips":  [],
    }
