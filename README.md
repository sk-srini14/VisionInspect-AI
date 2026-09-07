# VisionInspect-AI

AI-assisted smartphone-based mechanical component inspection, measurement and reporting.

## Objective

Build a browser-based inspection system that can:
- identify mechanical components;
- detect a known physical reference for scale calibration;
- measure suitable geometric dimensions;
- perform basic visual inspection;
- match detected fasteners against an engineering standards database;
- communicate confidence, uncertainty and measurement provenance;
- generate an inspection report.

## Engineering principle

AI is used where semantic interpretation is useful (component identification and visual anomaly recognition). Classical computer vision is used for deterministic geometry and measurement wherever possible.

The system should refuse to report a dimension when the image does not contain enough reliable information.

## Architecture

Smartphone camera
→ image quality assessment
→ AI component/reference detection
→ calibration
→ OpenCV feature detection
→ dimensional measurement
→ visual inspection
→ standards matching
→ confidence/uncertainty
→ PDF report

## Planned components

1. Hex bolt
2. Washer
3. Gear

## Measurement provenance

Every important result will be labelled as:
- AI detected
- CV measured
- database matched
- AI estimated

## Status

Phase 1 scaffold created. Measurement and inspection modules are intentionally implemented incrementally so each stage can be validated independently.
