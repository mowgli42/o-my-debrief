Feature: Post-mission analysis plots and PMR report
  As a mission analyst
  I want sensor collect geometry, weapons LAR compliance, and sensor health plots
  So that I can brief a multi-page after-action report with quantitative context

  Background:
    Given the o-my-debrief services are running (recorder, API, display)
    And the demo mission parquet for msn-demo-strike-recon is available via the API

  @api @analysis
  Scenario: Query sensor collect geometry analysis
    When I call GET /api/analysis/sensor-collects?mission=msn-demo-strike-recon
    Then the response lists collect points with range and footprint fields
    And metrics include success rate and collect counts

  @api @analysis
  Scenario: Query weapons release LAR compliance
    When I call GET /api/analysis/weapons-lar?mission=msn-demo-strike-recon
    Then the response lists at least one weapon release with LAR envelope fields
    And lar_summary includes in_lar and total counts

  @api @analysis
  Scenario: Query sensor telemetry time series
    When I call GET /api/analysis/sensor-telemetry?mission=msn-demo-strike-recon
    Then samples include sensor health and mode over mission time

  @ui @analysis
  Scenario: Analysis mode shows FOV, LAR, and sensor state plots
  # Manual / screenshot step forAnalysis mode
    Given I am on the debrief display for msn-demo-strike-recon
    When I enable Analysis view
    Then I see a sensor range vs footprint plot
    And I see weapons release points relative to the LAR envelope
    And I see time-aligned sensor health panels

  @report @pdf
  Scenario: Generate three-page Post Mission Report
    When I click Generate Post Mission Report (PDF)
    Then a print-ready HTML document opens with three pages
    And page 1 summarizes route, collections, and weapons
    And page 2 summarizes platform and sensor health
    And page 3 shows the FOV plot beside tasked vs collected and LAR notes