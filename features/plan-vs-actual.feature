Feature: Plan vs as-executed mission compare
  As a pilot or mission analyst
  I want to compare the briefed mission plan against the recorded as-executed events and route
  So that I can see paired actions despite slight timing skew, spot unplanned actions, and judge route adherence
  Without leaving the debrief workstation

  Background:
    Given the o-my-debrief services are running (API, display)
    And the demo mission parquet and mission plan sidecar are available via the API

  @api @plan
  Scenario: Demo mission exposes a mission plan distinct from as-executed
    Given fixtures exist for mission msn-demo-strike-recon
    When I call GET /api/plan?mission=msn-demo-strike-recon
    Then the response has available true
    And the response includes a non-empty planned route of lat/lon points
    And the response includes planned events with at least one planned strike and one planned collect
    And at least one planned event time differs from its closest as-executed peer

  @api @compare @fuzzy
  Scenario: Fuzzy compare pairs weapon releases despite slight time skew
    Given a mission plan with a planned strike and an as-executed EXECUTED strike on the same target within 90 seconds
    When I call GET /api/compare?mission=msn-demo-strike-recon&tolerance_seconds=90
    Then the pairs list includes a strike family pair linking those events
    And the pair delta_seconds is within 90

  @api @compare @unplanned
  Scenario: Unplanned as-executed action appears unmatched
    Given an as-executed collect or strike with no planned peer of the same family inside the tolerance
    When I call GET /api/compare?mission=msn-demo-strike-recon&tolerance_seconds=90
    Then that event appears in unmatched_actual

  @ui @timeline @compare
  Scenario: Stacked timeline shows plan above as-executed with linkages and unplanned glow
    Given I am on the debrief display for the demo mission
    When I open Compare view
    Then the mission plan timeline track appears above the as-executed track
    And paired like events are connected with linkage lines
    And unplanned as-executed markers are highlighted with a glowing icon
    When I enable the Hide mission plan slide toggle
    Then the plan track and linkage lines are hidden
    And the as-executed track remains visible

  @ui @map @plan-route
  Scenario: Map shows subdued planned route under actual track with toggle
    Given I am viewing the route map for the demo mission with a mission plan
    When the Show planned route toggle is on
    Then a subdued planned route polyline is drawn underneath the actual flown track
    When I turn the Show planned route toggle off
    Then the planned route is hidden
    And the actual flown track remains visible
