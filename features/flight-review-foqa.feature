Feature: Flight Review FOQA-style workspace
  As a platform engineer or mission analyst
  I want a synchronized flight review of air-data, health, and mission/sensor activity
  So that I can investigate platform and employment issues on one clock

  Background:
    Given the o-my-debrief services are running
    And the demo mission msn-demo-strike-recon is available

  @api @foqa
  Scenario: Query flight-review analysis
    When I call GET /api/analysis/flight-review?mission=msn-demo-strike-recon
    Then the response includes air_series, events, metrics, health_timeline, and planned_vs_actual
    And air_series samples include altitude, fuel, xte_nm, and cmd_alt_ft fields
    And metrics include exceedance_stats

  @api @foqa
  Scenario: Query fleet trends and flight performance report
    When I call GET /api/analysis/fleet-trends
    Then the response includes missions and aggregates
    When I call GET /api/report/flight-performance?mission=msn-demo-strike-recon
    Then the HTML includes five Flight Performance Report sections

  @ui @foqa
  Scenario: Flight Review mode keeps shared scrub clock
    Given I am on the debrief display for msn-demo-strike-recon
    When I open Flight Review mode
    Then I see synchronized track and air-data panels
    And I see planned-vs-actual, health timeline, and fleet trends
    When I scrub the timeline
    Then the air-data cursor follows the scrub time
    When I switch to ISR and return to Flight Review
    Then the scrub time is unchanged
