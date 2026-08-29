"""
ai/detection.py — Camera → YOLO detection stage.

Detects: person, helmet, mobile, safety_guard, PPE

This module is written against the real `ultralytics` YOLO API so it will
run unmodified against a real camera + trained weights in LIVE mode. It
never assumes internet access or bundled weights: if `ultralytics` or a
weights file (ai/model/*.pt) isn't available, `Detector` falls back to a
lightweight synthetic-detection generator so the rest of the AI pipeline
(tracking.py, rules.py) and the backend integration can still be exercised
end-to-end without a GPU, camera, or trained model — this is what powers
the platform's DEMO MODE for worker safety AI.

Real deployment:
    1. Train / obtain a YOLO model over the classes below and place the
       weights at ai/model/forgeguard_yolo.pt
    2. Set FORGEGUARD_AI_MODE=LIVE (see ai/rules.py CameraWorker) so a real
       cv2.VideoCapture / RTSP stream is read and passed through .detect()
"""
from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass, field
from typing import List

CLASS_NAMES = ["person", "helmet", "mobile", "safety_guard", "PPE"]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "forgeguard_yolo.pt")


@dataclass
class Detection:
    class_name: str
    confidence: float
    # x1, y1, x2, y2 in pixel coordinates of the source frame
    bbox: tuple[float, float, float, float]
    track_id: int | None = None


@dataclass
class FrameResult:
    frame_id: int
    timestamp: float
    detections: List[Detection] = field(default_factory=list)


class Detector:
    """Wraps a YOLO model (ultralytics) for the ForgeGuard detection classes.

    Falls back to a synthetic generator when no real model/weights are
    available, so `ai/`, the backend, and the frontend can all be
    demonstrated without hardware or a trained model.
    """

    def __init__(self, weights_path: str = MODEL_PATH, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._frame_counter = 0

        if os.path.exists(weights_path):
            try:
                from ultralytics import YOLO  # heavy import, only attempted if weights exist

                self.model = YOLO(weights_path)
            except Exception as exc:  # pragma: no cover - depends on optional heavy dep
                print(f"[ai.detection] Could not load YOLO weights ({exc}); using demo detector instead.")
        else:
            print(
                "[ai.detection] No trained weights found at "
                f"{weights_path}; running in DEMO detection mode. "
                "Provide real weights here for LIVE camera inference."
            )

    def detect(self, frame) -> FrameResult:
        """Run detection on a single video frame (numpy array from cv2).

        Returns a FrameResult with raw, untracked detections. Pass this to
        ai/tracking.py's ByteTrackWrapper to assign persistent track IDs.
        """
        self._frame_counter += 1
        if self.model is not None:
            return self._detect_real(frame)
        return self._detect_demo(frame)

    def _detect_real(self, frame) -> FrameResult:
        results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
        detections: List[Detection] = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                class_name = self.model.names.get(cls_id, str(cls_id))
                conf = float(box.conf[0])
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                detections.append(Detection(class_name, conf, (x1, y1, x2, y2)))
        return FrameResult(self._frame_counter, time.time(), detections)

    def _detect_demo(self, frame) -> FrameResult:
        """Synthetic but plausible detections: a person is (almost) always
        present, helmet/PPE/mobile presence toggles slowly so downstream
        persistence rules have something realistic to react to."""
        detections = [Detection("person", round(random.uniform(0.85, 0.99), 2), (100, 80, 380, 480))]

        if random.random() < 0.75:
            detections.append(Detection("helmet", round(random.uniform(0.7, 0.97), 2), (140, 80, 260, 160)))
        if random.random() < 0.6:
            detections.append(Detection("safety_guard", round(random.uniform(0.7, 0.95), 2), (100, 200, 380, 460)))
        if random.random() < 0.5:
            detections.append(Detection("PPE", round(random.uniform(0.7, 0.95), 2), (100, 200, 380, 460)))
        if random.random() < 0.08:
            detections.append(Detection("mobile", round(random.uniform(0.75, 0.96), 2), (220, 260, 280, 340)))

        return FrameResult(self._frame_counter, time.time(), detections)
