Feature: EO/IR ISR sensor performance and utilization dashboard
  As a sensor engineer or sensor operator
  I want a shared geospatial FOV view with engineering and utilization metrics
  So that I can relate technical sensor performance to collection effectiveness

  Background:
    Given the o-my-debrief services are running
    And the demo mission msn-demo-strike-recon is available

  @api @isr
  Scenario: Query EO/IR ISR analysis payload
    When I call GET /api/analysis/sensor-isr?mission=msn-demo-strike-recon
    Then the response includes fov_history, collections, detections, and opportunities
    And engineering and operator metric rollups are present

  @ui @isr
  Scenario: ISR mode shared map with Engineering and Operator perspectives
    Given I am on the debrief display for msn-demo-strike-recon
    When I open ISR mode
    Then I see the aircraft track with FOV footprints and collection overlays
    And Engineering mode shows uptime, pointing, quality, and fault metrics
    When I switch to Operator mode
    Then I see utilization metrics without losing the current scrub time
    When I select a collection or detection event
    Then the inspector shows correlated geometry, quality, and health