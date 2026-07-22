Feature: o-my Platform Debrief
  As a pilot or mission analyst
  I want to capture OMS bus messages from o-my during a mission (or sim) and later replay/scrub them in a visual debrief tool
  So that I can quickly see key milestones (sensor collects as diamonds, strikes as carets), understand what was collected/disseminated/struck/verified via BDA, and review platform state at critical times
  Without needing to parse raw logs or multiple separate tools

  Background:
    Given the o-my-debrief services are running (recorder, API, display)
    And a mission parquet dataset from o-my-sim or live o-my is available via the API

  @smoke @demo
  Scenario: Load demo mission and scrub timeline
    Given I am on the debrief display for a sample strike-recon mission
    When I select the mission and the timeline loads with event markers
    Then I see ◆ diamond markers for sensor collection events (color coded by EO/IR/SAR)
    And ▶ caret markers for strike task executions
    And the map shows the route waypoints and task locations
    When I scrub the timeline or click play
    Then the vehicle status panel updates fuel, datalink, payload, weapons loadout, and bay/gear status in sync
    And key milestones on the left highlight or scroll to the current time's events

  @recorder @parquet
  Scenario: Recorder captures OMS messages to Parquet
    Given o-my or o-my-sim is publishing to redis topics (systemstatus, sensorstatus, task, bda, etc.)
    When the data recorder starts with appropriate topic filters and output directory
    Then Parquet files are written with timestamped, typed messages (partitioned efficiently)
    And a manifest lists available missions/sessions
    And I can query the resulting parquet later via the API without data loss

  @api @swagger
  Scenario: Query milestones and state at time via Swagger-documented API
    Given the FastAPI reader is running and has loaded a mission's parquet
    When I use the Swagger UI or call GET /milestones?mission=xxx
    Then I receive a list of key events with times, types, and summaries (collections, strikes, BDA verifications, dissemination)
    When I call GET /state_at?time=...&mission=xxx
    Then I get interpolated or last-known platform state (fuel %, weapons bay status, active payload, datalink, weapons remaining) plus nearby events
    And the response schema is fully documented in OpenAPI

  @timeline @symbols
  Scenario: Timeline correctly distinguishes sensor collects (diamonds) from strike tasks (carets)
    Given a mission with both sensor collection events and strike task executions
    When the display renders the top timeline
    Then sensor events appear as ◆ diamonds (with sensor-type colors)
    And strike/attack tasks appear as ▶ carets or distinct arrow markers (with execution status colors)
    And hovering or clicking a marker updates the map selection and left milestones panel

  @map @tasks
  Scenario: Map displays route waypoints and overlays tasks with current-time context
    Given the mission route and task data are in the parquet (waypoints, collection points, strike coords)
    When viewing the center map panel
    Then the planned/actual route is shown as a polyline with labeled waypoints
    And sensor collects and strike points are overlaid as markers or footprints
    And as timeline scrubs, relevant overlays highlight or platform position indicator updates (if track available)

  @vehicle @status
  Scenario: Vehicle display reflects platform state changes over mission time
    Given systemStatus and related messages captured in parquet
    When I scrub to different mission phases
    Then Fuel gauge shows realistic depletion over time
    And Datalink indicator shows up/down status with last contact
    And Payload section lists active sensors/modes and last collect time
    And Weapons loadout shows initial vs remaining counts, with expended items noted by time
    And Landing gear / weapons bay indicators change state (e.g. bay opens before/during strike, closes after)
    And all values are consistent with the messages at or near the scrubbed time

  @milestones @left-panel
  Scenario: Key milestones panel provides stacked, clickable summary of mission outcomes
    Given a completed mission with collection, strike, and BDA events
    When the left panel renders
    Then it shows a chronological stack of high-value milestones (e.g. "EO Collect on TGT-042 ✓ disseminated", "Strike EXECUTED - munitions released", "BDA: target state verified neutralized")
    And each has timestamp, icon matching timeline symbol, outcome summary, and status
    When I click one
    Then timeline scrubs to that time, map centers on relevant location, and vehicle panel loads that instant's state

  @export @after-action
  Scenario: Export debrief artifacts for after-action review or reporting
    Given a reviewed mission debrief session
    When I click "Export Debrief Report" or similar
    Then I can download a PDF or structured JSON/CSV bundle containing timeline summary, milestones list, key vehicle states, map view (or description), and full event log
    And the export is suitable for inclusion in mission reports or import into other tools

  @integration @ecosystem
  Scenario: Recorder and display integrate with existing o-my / battlespace-manager workflows
    Given o-my is the source of OMS messages on redis
    When recorder runs as a companion process (or launched from battlespace-manager)
    Then captured data is immediately usable by the debrief API and display
    And the display can be opened as a separate window or tab from o-my C2 or battlespace-manager for post-mission review

# Additional scenarios for future: error handling on bad/missing parquet, multi-mission compare, AI-generated mission summary from milestones, full track animation from position messages, offline mode with bundled parquet, dark/light theme toggle, etc.