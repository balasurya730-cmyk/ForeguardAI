# AI Model Weights

Place a trained YOLO model here as `forgeguard_yolo.pt`.

The model should be trained on (at minimum) these classes, matching the
project's detection spec:

- person
- helmet
- mobile
- safety_guard
- PPE

If no weights file is present, `ai/detection.py`'s `Detector` automatically
falls back to a synthetic demo detector so the rest of the pipeline
(tracking, rule engine, backend integration, dashboard) can still be
exercised end-to-end without a trained model. This is what backs the
platform's DEMO MODE for worker safety AI.

## Training notes

A reasonable starting point is fine-tuning a pretrained YOLOv8n/s model
(via `ultralytics`) on a labeled dataset of factory-floor footage covering
the classes above. Suggested public building blocks:

- A general PPE/hard-hat detection dataset (helmet, person) as a base
- A small custom-labeled set of mobile-phone-in-hand frames from your own
  factory cameras for the `mobile` class, since phone-usage posture is
  environment-specific

Export the trained weights as `forgeguard_yolo.pt` and drop them in this
folder; no code changes are required — `Detector` will pick them up
automatically on the next backend/AI process restart.
