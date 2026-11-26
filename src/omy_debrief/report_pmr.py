"""Print-ready Post Mission Report HTML (3 pages)."""

from __future__ import annotations

import html
from typing import Any

from omy_debrief import store


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _fov_svg(points: list[dict[str, Any]], width: int = 320, height: int = 220) -> str:
    if not points:
        return f'<svg width="{width}" height="{height}"><text x="8" y="20" fill="#666">No collect geometry</text></svg>'
    xs = [float(p.get("slant_range_nm") or p.get("ground_range_nm") or 0) for p in points]
    ys = [
        float(
            p.get("footprint_diameter_m")
            or (p.get("footprint_area_km2") or 0) * 1000
            or (p.get("cone_angle_deg") or 0) * 50
        )
        for p in points
    ]
    pad = 28
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    if x0 == x1:
        x0 -= 1
        x1 += 1
    if y0 == y1:
        y0 -= 1
        y1 += 1

    def sx(v: float) -> float:
        return pad + (v - x0) / (x1 - x0) * (width - 2 * pad)

    def sy(v: float) -> float:
        return height - pad - (v - y0) / (y1 - y0) * (height - 2 * pad)

    colors = {"EO": "#4da3ff", "IR": "#ff5c6c", "SAR": "#5cd67e"}
    dots = []
    for p, x, y in zip(points, xs, ys):
        c = colors.get(str(p.get("sensor") or ""), "#3dd6c6")
        dots.append(
            f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="5" fill="{c}" opacity="0.85">'
            f'<title>{_esc(p.get("target_id"))} {x:.1f} nm</title></circle>'
        )
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:#0d1219;border:1px solid #2a3544">'
        f'<text x="{pad}" y="16" fill="#8b9cb0" font-size="10">Range (nm) →</text>'
        f'<text x="4" y="{height // 2}" fill="#8b9cb0" font-size="10" transform="rotate(-90 10,{height // 2})">'
        f"Footprint</text>"
        + "".join(dots)
        + "</svg>"
    )


def build_pmr_html(mission_id: str) -> str:
    manifest = store._manifest_for(mission_id)
    summary = store.mission_summary(mission_id)
    collects = store.sensor_collect_analysis(mission_id)
    lar = store.weapons_lar_analysis(mission_id)
    health = store.platform_health_summary(mission_id)
    stats = summary.get("stats") or {}
    analysis = summary.get("analysis") or {}

    wps = store.mission_waypoints(mission_id)
    wp_lines = "".join(
        f"<li>{_esc(w.get('label') or w.get('name') or 'WP')} — {_esc(w.get('lat'))}, {_esc(w.get('lon'))}</li>"
        for w in wps[:8]
    )
    if not wp_lines:
        wp_lines = "<li>See flown track in debrief map</li>"

    strike_lines = ""
    for r in lar.get("releases") or []:
        flag = "✓ in LAR" if r.get("within_lar") else "✗ outside LAR"
        strike_lines += (
            f"<li>{_esc(r.get('timestamp'))} · {_esc(r.get('task_id'))} "
            f"— {flag} · range {_esc(r.get('release_slant_range_nm'))} nm</li>"
        )
    if not strike_lines:
        strike_lines = "<li>No weapon releases recorded</li>"

    deg = health.get("degradations") or []
    deg_html = (
        "".join(f"<li>{_esc(d)}</li>" for d in deg) if deg else "<li>No major degradations logged</li>"
    )

    svg = _fov_svg(collects.get("points") or [])
    metrics = collects.get("metrics") or {}
    lar_sum = lar.get("lar_summary") or {}

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Post Mission Report — {_esc(manifest.name)}</title>
  <style>
    @page {{ size: letter; margin: 0.65in; }}
    body {{ font-family: system-ui, sans-serif; color: #1a1a1a; margin: 0; }}
    h1 {{ font-size: 18pt; margin: 0 0 8px; }}
    h2 {{ font-size: 13pt; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
    .page {{ page-break-after: always; min-height: 9.2in; }}
    .page:last-child {{ page-break-after: auto; }}
    ul {{ margin: 6px 0; padding-left: 18px; }}
    .meta {{ font-size: 10pt; color: #555; }}
    .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 12px; }}
    .box {{ border: 1px solid #ddd; padding: 10px; border-radius: 4px; }}
    .stat {{ font-size: 11pt; margin: 4px 0; }}
    @media print {{
      .noprint {{ display: none; }}
    }}
  </style>
</head>
<body>
  <p class="noprint"><button onclick="window.print()">Print / Save as PDF</button></p>

  <section class="page" id="page-1-mission-overview">
    <h1>Post Mission Report</h1>
    <p class="meta">Mission {_esc(manifest.name)} ({_esc(mission_id)}) · {_esc(manifest.platform_callsign)}<br/>
    Window {_esc(manifest.start_time)} → {_esc(manifest.end_time)}</p>
    <h2>Mission Overview</h2>
    <p><strong>Route / waypoints</strong></p>
    <ul>{wp_lines}</ul>
    <p><strong>Sensor collections</strong></p>
    <ul>
      <li>Successful collects: {_esc(metrics.get('collected'))} / {_esc(metrics.get('attempted'))}</li>
      <li>Success rate: {float(metrics.get('success_rate') or 0) * 100:.0f}%</li>
      <li>Tasked vs collected: {_esc(metrics.get('tasked_planned'))} planned · {_esc(metrics.get('unplanned'))} unplanned actual</li>
      <li>Disseminations: {_esc(stats.get('disseminations'))}</li>
    </ul>
    <p><strong>Weapons releases</strong></p>
    <ul>{strike_lines}</ul>
    <p class="meta">Strikes executed: {_esc(stats.get('strikes_executed'))} · BDA: {_esc(stats.get('bda_reports'))}</p>
  </section>

  <section class="page" id="page-2-platform-sensor-health">
    <h2>Platform and Sensor Health</h2>
    <p><strong>Operational status</strong></p>
    <ul>
      <li>Platform readiness uptime: {float(health.get('readiness_uptime_pct') or 0):.0f}% GREEN</li>
      <li>Datalink uptime: {float(health.get('datalink_uptime_pct') or 0):.0f}%</li>
      <li>Sensor telemetry uptime: {float(health.get('sensor_uptime_pct') or 0):.0f}% OK/WARN</li>
    </ul>
    <p><strong>Key degradations</strong></p>
    <ul>{deg_html}</ul>
    <p><strong>Assessment</strong></p>
    <p>{_esc(health.get('narrative'))}</p>
  </section>

  <section class="page" id="page-3-fov-details">
    <h2>Collection geometry &amp; dissemination</h2>
    <div class="cols">
      <div class="box">
        <p><strong>Sensor range vs footprint</strong></p>
        {svg}
      </div>
      <div class="box">
        <p class="stat"><strong>Uptime</strong> — datalink {float(health.get('datalink_uptime_pct') or 0):.0f}% · sensors {float(health.get('sensor_uptime_pct') or 0):.0f}%</p>
        <p class="stat"><strong>Tasked vs collected</strong> — {float(metrics.get('tasked_collected_pct') or 0) * 100:.0f}% of planned collects matched</p>
        <p class="stat"><strong>Products disseminated</strong> — {float(analysis.get('product_volume_gb') or 0):.1f} GB total (demo)</p>
        <p class="stat"><strong>LAR compliance</strong> — {int(lar_sum.get('in_lar') or 0)} / {int(lar_sum.get('total') or 0)} releases inside LAR</p>
        <p class="stat"><strong>Notes</strong> — {_esc(analysis.get('lar_notes') or 'All demo releases within envelope.')}</p>
      </div>
    </div>
  </section>
</body>
</html>"""