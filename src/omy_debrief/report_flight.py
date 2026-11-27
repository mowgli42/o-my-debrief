"""Five-section Aircraft Flight Performance Report (FOQA-style summary)."""

from __future__ import annotations

import html
from typing import Any

from omy_debrief import store


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def build_flight_performance_html(mission_id: str) -> str:
    m = store._manifest_for(mission_id)
    fr = store.flight_review_analysis(mission_id)
    health = store.platform_health_summary(mission_id)
    summary = store.mission_summary(mission_id)
    met = fr.get("metrics") or {}
    pva = fr.get("planned_vs_actual") or {}
    sensor = fr.get("sensor_strip") or {}
    stats = summary.get("stats") or {}
    events = fr.get("events") or []
    exceed = met.get("exceedance_stats") or {}

    event_rows = "".join(
        f"<tr><td>{_esc(e.get('timestamp'))}</td><td>{_esc(e.get('severity'))}</td>"
        f"<td>{_esc(e.get('title'))}</td><td>{_esc(e.get('detail'))}</td></tr>"
        for e in events[:12]
    ) or "<tr><td colspan='4'>No FOQA events</td></tr>"

    exceed_li = "".join(
        f"<li>{_esc(k)}: {_esc(v)}</li>" for k, v in sorted(exceed.items())
    ) or "<li>None</li>"

    assessment = []
    assessment.append("Aircraft completed the recorded mission window.")
    if met.get("warn_count"):
        assessment.append(
            f"{met['warn_count']} WARN FOQA event(s) require engineering review."
        )
    if pva.get("max_xte_nm") and float(pva["max_xte_nm"]) > 0.8:
        assessment.append("Cross-track error exceeded envelope on at least one sample.")
    else:
        assessment.append("Route tracking remained within demo XTE envelope for most samples.")
    if sensor.get("opportunities_unused"):
        assessment.append(
            f"{sensor['opportunities_unused']} unused sensor opportunities noted (employment, not automatic fail)."
        )
    if stats.get("strikes_executed"):
        assessment.append(
            f"Strike executions: {stats.get('strikes_executed')}; BDA reports: {stats.get('bda_reports')}."
        )
    assessment_html = "".join(f"<li>{_esc(a)}</li>" for a in assessment)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Aircraft Flight Performance Report — {_esc(m.name)}</title>
  <style>
    @page {{ size: letter; margin: 0.65in; }}
    body {{ font-family: system-ui, sans-serif; color: #1a1a1a; margin: 0; }}
    h1 {{ font-size: 18pt; margin: 0 0 6px; }}
    h2 {{ font-size: 12pt; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 18px; }}
    .meta {{ font-size: 10pt; color: #555; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 10pt; }}
    th, td {{ border: 1px solid #ddd; padding: 4px 6px; text-align: left; }}
    th {{ background: #f4f4f4; }}
    ul {{ margin: 6px 0; padding-left: 18px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .box {{ border: 1px solid #ddd; padding: 10px; border-radius: 4px; }}
    @media print {{ .noprint {{ display: none; }} }}
  </style>
</head>
<body>
  <p class="noprint"><button onclick="window.print()">Print / Save as PDF</button></p>
  <h1>Aircraft Flight Performance Report</h1>
  <p class="meta">POST-FLIGHT DEBRIEF · {_esc(m.name)} ({_esc(mission_id)}) · {_esc(m.platform_callsign)}<br/>
  {_esc(m.start_time)} → {_esc(m.end_time)}</p>

  <h2>1. Flight overview</h2>
  <div class="grid">
    <div class="box">
      <ul>
        <li>Flight duration: {_esc(met.get('duration_min'))} min</li>
        <li>Max / min altitude: {_esc(met.get('max_alt_ft'))} / {_esc(met.get('min_alt_ft'))} ft</li>
        <li>Fuel: {_esc(met.get('fuel_start_pct'))}% → {_esc(met.get('fuel_end_pct'))}% (burn {_esc(met.get('fuel_burn_pct'))}%)</li>
        <li>Samples: {_esc(met.get('samples'))}</li>
      </ul>
    </div>
    <div class="box">
      <ul>
        <li>Mean XTE: {_esc(pva.get('mean_xte_nm'))} nm · max {_esc(pva.get('max_xte_nm'))} nm</li>
        <li>Mean |alt error|: {_esc(pva.get('mean_abs_alt_error_ft'))} ft</li>
        <li>Mean |spd error|: {_esc(pva.get('mean_abs_spd_error_kts'))} kts</li>
        <li>Plan available: {_esc(pva.get('available'))}</li>
      </ul>
    </div>
  </div>

  <h2>2. Aircraft performance</h2>
  <table>
    <tr><th>Parameter</th><th>Result</th></tr>
    <tr><td>Fuel burn</td><td>{_esc(met.get('fuel_burn_pct'))}%</td></tr>
    <tr><td>Max altitude</td><td>{_esc(met.get('max_alt_ft'))} ft</td></tr>
    <tr><td>Mean XTE</td><td>{_esc(pva.get('mean_xte_nm'))} nm</td></tr>
    <tr><td>FOQA WARN events</td><td>{_esc(met.get('warn_count'))}</td></tr>
    <tr><td>Total FOQA events</td><td>{_esc(met.get('event_count'))}</td></tr>
  </table>

  <h2>3. Systems health</h2>
  <ul>
    <li>Platform readiness uptime: {float(health.get('readiness_uptime_pct') or 0):.0f}%</li>
    <li>Datalink uptime: {float(health.get('datalink_uptime_pct') or 0):.0f}%</li>
    <li>Sensor telemetry uptime: {float(health.get('sensor_uptime_pct') or 0):.0f}%</li>
    <li>Exceedances: <ul>{exceed_li}</ul></li>
  </ul>
  <p>{_esc(health.get('narrative'))}</p>

  <h2>4. Mission execution</h2>
  <ul>
    <li>Collections: {_esc(sensor.get('collections'))} · detections {_esc(sensor.get('detections'))}</li>
    <li>Unused opportunities: {_esc(sensor.get('opportunities_unused'))}</li>
    <li>Sensor uptime: {_esc(sensor.get('sensor_uptime_pct'))}%</li>
    <li>Strikes executed: {_esc(stats.get('strikes_executed'))} · BDA: {_esc(stats.get('bda_reports'))}</li>
    <li>Disseminations: {_esc(stats.get('disseminations'))}</li>
  </ul>

  <h2>5. Post-flight assessment</h2>
  <ul>{assessment_html}</ul>

  <h2>FOQA event log (excerpt)</h2>
  <table>
    <tr><th>Time</th><th>Sev</th><th>Title</th><th>Detail</th></tr>
    {event_rows}
  </table>
</body>
</html>"""