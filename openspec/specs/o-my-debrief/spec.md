# o-my Platform Debrief

## Purpose

The o-my Platform Debrief extends the Open Arsenal o-my (and related o-my-sim, battlespace-manager) ecosystem with a dedicated capability to capture, persist, query, and visualize OMS (Open Mission Services) bus messages. This enables pilots, mission commanders, and analysts to rapidly reconstruct and understand key mission milestones and outcomes from tasking and platform activity.

Core value: Transform raw OMS telemetry (systemStatus, sensorStatus, task updates, collection events, strike execution, BDA reports, etc.) into an intuitive, time-synced debrief experience. Answer questions like:

- What was collected and when (sensor events with diamonds on timeline)?
- Was data disseminated successfully?
- Were strike tasks executed, and with what results?
- Did BDA verify target state post-strike?
- What was the platform state (fuel, weapons, payload, datalink, bay/gear) at critical moments?

The system comprises three integrated tools:

1. **Data Recorder**: Listens to o-my Redis topics (OMS bus), serializes relevant messages to efficient, queryable Parquet format (partitioned by time/mission).
2. **Parquet Data Reader (FastAPI)**: Provides a documented Swagger/OpenAPI interface to query the stored data by absolute or relative time, filter by event type or milestone, retrieve full context at a timestamp, and expose key aggregated milestones.
3. **Debrief Display (Web UI)**: Svelte-based rich client that consumes the API and renders a military-style debrief workstation: interactive timeline, milestone list, geospatial map with tasks/waypoints, and live vehicle/platform status panel. Supports scrubbing, filtering, and export for after-action reports.

Designed to run locally or in containerized environments alongside o-my instances (real or simulated via o-my-sim). Follows established patterns from fuzzy-reconciler, battlespace-manager: OpenSpec-driven development, Gherkin features, Beads workflow integration, Svelte + FastAPI + Docker/Kamal deploy, local-first with minimal external deps.

Integrates with existing OMS/UCI schemas used in o-my and o-my-sim for message compatibility. Parquet chosen for columnar efficiency on time-series sensor/task data, fast queries on large logs without needing a full timeseries DB for MVP.

## Requirements

### Requirement: OMS Message Capture and Parquet Persistence (Data Recorder)

The recorder SHALL subscribe to configurable Redis topics/channels from an o-my instance (or sim) carrying OMS messages such as:

- systemStatus / platformStatus (fuel, health, config, gear/bay states, datalink)
- sensorStatus / sensorCollection (events with timestamps, sensor type, target/coords, collection params, success/failure)
- task / taskingStatus (planned, assigned, in-progress, completed; strike tasks with effects)
- dissemination / dataLink events
- BDA / verification reports
- Other relevant: waypoint progress, payload status, weapons inventory changes

It SHALL parse messages according to the OMS/UCI schema (reference o-my and o-my-sim definitions), enrich with receive timestamp if needed, and append to time-partitioned Parquet datasets (e.g., dataset root partitioned by mission_id/date/hour or flat with metadata columns for efficient filtering).

Storage format: Parquet with appropriate schema (timestamp, msg_type, source, payload JSON or flattened columns for common fields, raw_blob optional for fidelity). Support append-only or rolling files. Configurable retention or mission-based file sets.

Optional: Live mode (tail redis and write continuously) and batch/replay mode (process recorded redis streams or log files).

#### Scenario: Capture during simulated mission in o-my-sim

- **GIVEN** o-my-sim is publishing realistic OMS messages to redis topics for a strike-recon mission (sensor collects on waypoints, task execution, BDA)
- **WHEN** the recorder is started against the same redis instance with topic filters for systemstatus,sensorstatus,task,*
- **THEN** parquet files are created/updated in ./data/debrief/ with messages timestamped and typed
- **AND** a manifest or index file tracks missions/sessions available
- **AND** no messages lost; high fidelity preserved for later query

### Requirement: Time-Aware Parquet Query API (FastAPI + Swagger)

A FastAPI service SHALL expose the stored Parquet data via a clean, versioned REST API with full OpenAPI/Swagger documentation.

Key capabilities:
- List available missions/sessions (from parquet metadata or sidecar index)
- Query events in a time window: GET /events?mission=xxx&start=ISO&end=ISO&type=sensor,strike or POST /query with JSON body for complex filters (event_types list, geo bbox, keyword in payload, etc.)
- Get state snapshot at exact time: /state_at?time=...&mission=...  (interpolates or last-known for continuous states like fuel, position; lists discrete events around it)
- Milestone extraction: /milestones?mission=...  or filtered, returning curated list of high-value events (e.g. "first_sensor_collect", "strike_executed", "bda_positive", "datalink_lost") with times, summaries, links to raw messages. The API or a helper layer computes/ tags these based on rules or config (e.g. task status transitions to "executed", sensor success + coords present = collection event)
- Raw message replay or full context at time T
- Aggregates: counts per type, timeline summary buckets, etc. for UI perf
- Health, metrics endpoints

Use pyarrow or polars for efficient reads (predicate pushdown on partitions/timestamps). Pydantic models for requests/responses. Support CORS for local web UI. Optional auth (none for localhost dev).

Swagger UI at /docs for interactive testing and as living docs. Can be called from other tools (e.g. battlespace-manager extensions, custom scripts, or even o-my C2 plugins).

#### Scenario: Query key events around a strike time

- **GIVEN** parquet from a completed mission with multiple sensor collects, one strike task, and BDA report
- **WHEN** client calls /milestones?mission=msn-2026-07-21 or /events?start=...&end=...&types=strike,bda,sensor
- **THEN** returns structured list with timestamps, types, short descriptions (e.g. "EO sensor collected image set on target TGT-042 at 14:22:05"), classification or tags, and reference to full message IDs
- **AND** /state_at?time=2026-07-21T14:25:00Z returns fuel=68%, weapons_bay=open, active_datalink=true, current_payload=EO, lat/lon approx, recent events summary

### Requirement: Rich Interactive Debrief Web Display (Svelte Frontend)

The display tool SHALL be a self-contained or co-served Svelte 5 application (Vite build) that provides an at-a-glance yet deep-dive mission debrief interface. It consumes the Parquet Reader API exclusively (no direct parquet access from browser).

**Primary Layout (desktop-first, responsive down to tablet; dark tactical theme with accent colors for event types):**

- **Header / Mission Selector + Time Scrubber**: Top bar with mission dropdown or list, current sim/real time display, large horizontal timeline/scrubber bar spanning mission duration. Play/pause button for animated replay (advances time, updates all panels). Zoomable/pannable timeline. 

  Event markers overlaid:
  - **Diamonds (◆)** : Sensor collection / data capture events. Color-coded by sensor (EO blue, IR red, SAR green, etc.). Size or label for volume/importance. Hover/click shows brief info, jumps time and highlights related milestone/map.
  - **Carets / Arrows (▶ or caret symbols)** : Strike / kinetic task executions or weapon releases. Different style/color for planned vs. executed vs. verified. Perhaps stacked or with status (success/fail).
  - Other markers: dissemination events (circles?), status changes, BDA (check or flag), datalink events.

  Clicking marker or scrubbing updates the "current time" globally, which drives map, vehicle panel, and highlights active/near milestones.

- **Left Panel: Key Milestones (stacked vertical)**: Scrollable or accordion list of curated high-signal events/milestones in chronological order. Each entry: timestamp | icon (matching timeline symbol) | short title + outcome (e.g. "Sensor Collect ✓ | EO on TGT-042 | 3 images, 2.1GB disseminated") | status badge (completed, verified, pending BDA). 

  Click to scrub timeline to that instant + center map on relevant location + load context in other panels. "Expand" for raw message summary or link to full inspector.

  Milestones derived/enriched by the backend (or client-side rules) from raw events: e.g. task transition to EXECUTED + effects reported = strike milestone; sensor success + payload hash or file ref = collect; subsequent BDA report linked by target ID = verification milestone.

- **Center: Geospatial Map with Route & Tasks**: Interactive map (Leaflet/MapLibre GL via lightweight Svelte wrapper or vanilla). 

  - Displays planned or actual flight route as polyline with waypoint markers (numbered or labeled).
  - Overlays task locations (strike points as special icons, sensor collection footprints as polygons or circles with transparency).
  - Dynamic elements at current time: current platform position (if track data available in messages; otherwise last known or interpolated), sensor field-of-view or last collection point highlighted, weapons impact or BDA point.
  - Clickable elements: waypoint -> show task details or scrub to arrival time; collection point -> highlight diamond on timeline and milestone.
  - Layers toggle: Route, Waypoints, Sensor Events, Strike Points, BDA, Current Position Track (if multi-point).
  - Simple basemap (OSM or neutral military-style tiles if available locally/offline option).

  Note: For full track replay, the recorder/API should also capture position updates if present in systemStatus or dedicated nav messages; MVP can use waypoint progress or assume track from tasks.

- **Right / Bottom Panel: Vehicle & Platform Status (at current scrubbed time)**: Dashboard-style cards or grouped indicators mimicking aircraft MFD (Multi-Function Display) or mission computer readouts. Use Tailwind + heroicons/lucide or custom SVG for professional look. Real-time feel as time changes.

  Specific elements requested:
  - **Fuel / Endurance**: Horizontal or circular progress bar/gauge showing % remaining or time-to-bingo. Color scale (green > yellow > red). Perhaps trend arrow if history.
  - **Active Datalink**: Status indicator (green "LINK UP - 4.2 Mbps" or red "LINK DOWN", last contact time). Icon for satellite/link type if available.
  - **Payload Status**: List or icons of active sensors/payloads (EO/IR/SAR/MTI etc.), mode (search/track), health (OK/WARN/FAIL), last collection timestamp or status.
  - **Weapons Loadout**: Table or visual rack: missile/bomb types, quantities remaining vs. initial. Expended highlighted or struck-through with timestamp of release if known. Perhaps "expended: 2x GBU-XXX at 14:25".
  - **Landing Gear / Weapons Bay Openings**: Status icons or animated indicators (gear up/down, bay doors open/closed). Perhaps with last command time or current config from systemStatus. Color or shape change on state change. (E.g., bay open icon during strike window).

  Additional helpful: Current lat/lon/alt/heading/speed (if in messages), overall platform health summary, alerts/warnings active at that time.

  The panel updates smoothly on scrub without full reload; perhaps smooth transitions or just instant update since data is local/fast.

**Additional UI/UX Features:**

- Global time control affects all synced views.
- Event log / raw inspector modal or drawer: searchable table of all messages in window, with JSON pretty view on select. Filterable by type.
- Filters sidebar or top: toggle visibility of event types on timeline/map, search milestones.
- Export: "Generate Debrief Report" button -> PDF (via browser print or jsPDF) or JSON bundle with timeline image? summary milestones, map screenshot (html2canvas), key vehicle states, full event CSV. Or simple "Export Timeline + Milestones (JSON/CSV)".
- Keyboard: Arrow keys or space to scrub/play, number keys jump to milestones, esc close modals.
- Responsive: On narrower screens, collapse to tabs (Timeline+Map | Milestones | Status) or stacked.
- Theming: Dark navy/charcoal bg, cyan/amber/orange accents for events (blue collect, red strike, green verified), high contrast text, subtle gridlines on timeline/map. Professional, not gamified.
- Performance: Virtualized lists for long missions (hundreds of events), efficient re-renders on scrub (Svelte 5 runes or stores), map clustering or LOD if many points.
- Demo mode: Load bundled sample parquet or API demo data simulating a short recon-strike mission with 5-6 sensor collects, 1-2 strikes, BDA, status changes (fuel drop, bay open/close, weapons count change, datalink flicker).

#### Scenario: Full end-to-end debrief session for a completed strike mission

- **GIVEN** recorder has captured a full o-my-sim mission parquet dataset; API running; display loaded in browser pointing to API
- **WHEN** user selects the mission and scrubs timeline or hits play
- **THEN** timeline populates with ◆ sensor collects at various times and ▶ strike task(s)
- **AND** left milestones list shows ordered key events including "Initial EO collection on TGT-042", "Data disseminated to ground", "Strike task EXECUTED - 2x munitions released", "BDA report: target neutralized - verified"
- **AND** map shows route waypoints, highlights collection points and strike location; as time scrubs, platform icon moves (or snaps to relevant), task markers activate
- **AND** vehicle panel updates: at pre-strike time fuel shows high, bay closed, full loadout; during strike window: bay opens, weapons count decreases, fuel slightly lower; post: bay closed?, BDA linked
- **AND** clicking a milestone or diamond centers map and shows details; export produces usable after-action artifact

### Requirement: Integration, Deployment, and Extensibility

- **Integration with Open Arsenal ecosystem**: Recorder can be run as sidecar to o-my or launched from battlespace-manager / o-my C2. Display can be embedded or linked from existing UIs. Uses same message schemas and redis patterns. Future: direct OMS bus tap or extension of existing logging in o-my.
- **Deployment**: Single docker compose up brings up recorder (optional live), API, and frontend (or frontend static served by FastAPI). Or separate services. Supports Kamal deploy for VPS. Local dev: make dev runs API + Vite HMR.
- **Data model & schema alignment**: Leverage or extend OMS message definitions from o-my/o-my-sim. Parquet schema flexible (JSON columns for complex payloads + extracted common fields like event_time, event_type, target_id, coords, status). Include provenance (source topic, original msg id/timestamp).
- **Extensibility**: Config-driven event classifiers for milestones (YAML/JSON rules: if msg_type==task and status==EXECUTED and effects.reported -> milestone "strike_executed"). Pluggable visualizers or additional panels (e.g. comms log, sensor product thumbnails if paths available). Hook for AI-assisted summary generation (local LLM on milestones + context? future).
- **Non-functional**: 
  - Query perf: <1s for typical mission queries even with 10k+ messages.
  - Storage: Parquet highly compressible; 1h mission at 10Hz status ~ few MB.
  - Usability: Intuitive for pilots/analysts familiar with military debrief tools (timeline scrubbing like video players or mission replay stations).
  - Testability: Gherkin scenarios map to E2E (Playwright) for UI flows; unit tests for recorder parsing and API query logic; sample data generators.
  - Security: Localhost default; optional token or network ACL. No PII assumption; user handles classification/sensitivity of mission data.

## Implementation Guidance

Follow the established OpenSpec + Gherkin + Beads + Cursor workflow from fuzzy-reconciler and schwerpunkt.

1. Initialize repo with this spec at openspec/specs/o-my-debrief/spec.md and corresponding Gherkin in features/.
2. Use Beads to break Requirements into actionable issues/stories (e.g., "Implement Parquet recorder service", "Build FastAPI query layer with time and milestone endpoints", "Svelte timeline component with diamond/caret markers", "Map + vehicle status panels synced to time", "Docker compose and dev Makefile").
3. Tech stack alignment:
   - Recorder: Python (asyncio + redis-py or aioredis), pyarrow/pandas or polars for write, watchdog or scheduled for rolling files. Config via env/CLI (redis url, topics list, output dir, mission tag).
   - API: FastAPI + uvicorn, pyarrow for reads + fast filters, Pydantic, perhaps fastapi-cache or simple. Swagger auto.
   - Frontend: Svelte 5 + Vite + Tailwind + shadcn-svelte or daisyUI for components. For timeline: custom SVG + pointer events or library like vis-timeline / timelinejs (light) or d3-time. Map: svelte-leaflet or @maplibre + svelte. Icons: lucide-svelte or heroicons. State: Svelte stores + URL for deep linkable time/mission.
   - Shared: OMS message models (perhaps shared lib or copy from o-my if accessible; or define minimal Pydantic subset). Common docker base.
4. MVP prioritization (per OpenSpec guidance): Get recorder writing parquet from redis (or simulated messages) → API serving /events and /state_at for a demo dataset → Basic Svelte shell with timeline (static markers) + map (static route) + status cards updating on scrub → Wire to live API → Add milestone extraction logic and left panel → Polish symbols, interactions, export, demo data generator.
5. Later phases: Full track replay from position messages, AI summary of mission (local model on events), integration hooks (e.g. publish debrief artifacts back to o-my or battlespace DB), multi-mission compare, VR/AR extensions? (stretch).

This spec is the source of truth. Scenarios in the companion .feature file provide BDD tests and acceptance criteria. Implementation can proceed immediately with AI coding agents following the beads/openspec patterns.

**Status**: specified (ready for beads issue breakdown and phased implementation)

**Related**: o-my (core OMS C2), o-my-sim (message generation for testing), battlespace-manager (potential consumer or extension point), fuzzy-reconciler (reference for OpenSpec/Svelte/FastAPI patterns), Schwerpunkt (for any agentic extensions to milestone detection or summarization).

---

*Open Arsenal — Open by Design • Agile by Default*