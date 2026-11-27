# Change: Airborne EO/IR ISR Sensor Performance & Utilization Dashboard

## Why

Sensor engineers and operators need a shared geospatial picture that connects
EO/IR technical health with how the sensor was actually employed—FOV footprints,
detections, successful vs missed collections, pointing performance, and faults—
without leaving the debrief station.

## What changes

- Demo mission gains EO/IR ISR samples: pointing (commanded vs actual), IFOV/FOR
  footprints, detections, collection quality, unused opportunities, and faults.
- API: `GET /api/analysis/sensor-isr?mission=` returning geospatial series,
  engineering metrics, operator utilization metrics, and correlatable events.
- UI **ISR** mode: large shared Leaflet map (track, pointing, historical FOVs,
  detections, collections, uncollected opportunities) plus Engineering / Operator
  perspective panels that keep geographic + temporal context when switching.
- Timeline scrub remains the clock; selecting an ISR event updates map highlight
  and inspector (geometry, quality, health, success/failure).

## Non-goals

- Live closed-loop gimbal control or re-tasking
- Full photogrammetric ortho / stereo reconstruction
- Multi-sensor fusion across platforms
- Replacing the existing Analysis (FOV scatter / LAR) or Compare views
- Embedding sensor video in the ISR map (pop-out viewer remains separate)