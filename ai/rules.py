"""
ai/rules.py — Rule Engine stage + camera worker orchestration.

Turns raw, tracked, per-frame detections into confirmed safety violations
using *persistence* logic: a condition (no helmet, mobile present) must
hold continuously for a configured duration before a violation event is
created. This avoids false positives from a single noisy frame (e.g. a
helmet briefly occluded).

Design principle (mobile detection): the system detects visual phone
presence and persistence only. It does not claim to infer worker intent.

Pipeline:
    Camera -> Detector (detection.py) -> ByteTrackWrapper (tracking.py)
            -> RuleEngine (this file) -> POST /api/safety/events -> backend

Run standalone against a real camera in LIVE mode:
    python -m ai.rules --camera-id 1 --source 0
(source can be a webcam index, RTSP URL, or video file path)
"""
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

import requests

from ai.detection import Detector, FrameResult
from ai.tracking import ByteTrackWrapper

# How long (seconds) a condition must persist before it becomes a violation.
HELMET_MISSING_PERSISTENCE_SECONDS = 5.0
PPE_MISSING_PERSISTENCE_SECONDS = 5.0
MOBILE_PERSISTENCE_SECONDS = 4.0  # "3-5 seconds" per spec

BACKEND_BASE_URL = "http://localhost:8000"


@dataclass
class _WorkerConditionState:
    helmet_missing_since: Optional[float] = None
    ppe_missing_since: Optional[float] = None
    mobile_present_since: Optional[float] = None
    reported_helmet: bool = False
    reported_ppe: bool = False
    reported_mobile: bool = False


class RuleEngine:
    """Applies persistence rules per tracked worker (track_id) and reports
    confirmed violations to the backend's /api/safety/events endpoint."""

    def __init__(self, camera_id: int, backend_url: str = BACKEND_BASE_URL, worker_id_map: Optional[Dict[int, int]] = None):
        self.camera_id = camera_id
        self.backend_url = backend_url
        # Maps a tracker's local track_id -> a real Worker.id in the database.
        # In a real deployment this comes from a face/badge re-identification
        # step; for demo/testing it can be an identity map or left as None
        # (violations are still recorded, just without a linked worker).
        self.worker_id_map = worker_id_map or {}
        self._state: Dict[int, _WorkerConditionState] = {}

    def process(self, frame_result: FrameResult):
        now = frame_result.timestamp
        people = [d for d in frame_result.detections if d.class_name == "person" and d.track_id is not None]

        for person in people:
            track_id = person.track_id
            state = self._state.setdefault(track_id, _WorkerConditionState())

            worker_detections = [d for d in frame_result.detections if d.track_id == track_id]
            has_helmet = any(d.class_name == "helmet" for d in worker_detections)
            has_ppe = any(d.class_name in ("PPE", "safety_guard") for d in worker_detections)
            has_mobile = any(d.class_name == "mobile" for d in worker_detections)

            self._apply_persistence(
                now, state, "helmet_missing_since", "reported_helmet",
                condition_active=not has_helmet,
                persistence_seconds=HELMET_MISSING_PERSISTENCE_SECONDS,
                on_confirmed=lambda duration: self._report_violation(
                    track_id, "NO_HELMET", confidence=person.confidence, duration_seconds=duration,
                ),
            )
            self._apply_persistence(
                now, state, "ppe_missing_since", "reported_ppe",
                condition_active=not has_ppe,
                persistence_seconds=PPE_MISSING_PERSISTENCE_SECONDS,
                on_confirmed=lambda duration: self._report_violation(
                    track_id, "NO_PPE", confidence=person.confidence, duration_seconds=duration,
                ),
            )
            self._apply_persistence(
                now, state, "mobile_present_since", "reported_mobile",
                condition_active=has_mobile,
                persistence_seconds=MOBILE_PERSISTENCE_SECONDS,
                on_confirmed=lambda duration: self._report_violation(
                    track_id, "MOBILE_USAGE", confidence=person.confidence, duration_seconds=duration,
                ),
            )

    @staticmethod
    def _apply_persistence(now, state, since_field, reported_field, condition_active, persistence_seconds, on_confirmed):
        since = getattr(state, since_field)
        if condition_active:
            if since is None:
                setattr(state, since_field, now)
            else:
                duration = now - since
                if duration >= persistence_seconds and not getattr(state, reported_field):
                    setattr(state, reported_field, True)
                    on_confirmed(duration)
        else:
            setattr(state, since_field, None)
            setattr(state, reported_field, False)

    def _report_violation(self, track_id: int, violation_type: str, confidence: float, duration_seconds: float):
        worker_id = self.worker_id_map.get(track_id)
        payload = {
            "worker_id": worker_id,
            "camera_id": self.camera_id,
            "violation_type": violation_type,
            "confidence": confidence,
            "duration_seconds": round(duration_seconds, 1),
            "evidence_path": None,  # populated by save_evidence_frame() in a real deployment
        }
        try:
            resp = requests.post(f"{self.backend_url}/api/safety/events", json=payload, timeout=5)
            resp.raise_for_status()
            print(f"[ai.rules] Reported {violation_type} for track {track_id} (worker {worker_id}): {resp.status_code}")
        except requests.RequestException as exc:
            print(f"[ai.rules] Failed to report violation to backend: {exc}")


class CameraWorker:
    """Ties detection + tracking + rules together for one camera stream.

    In LIVE mode, `source` is a webcam index / RTSP URL / video file read
    via OpenCV. In DEMO mode (no `source`), synthetic frames are used so
    the full AI pipeline can run without a camera (Detector already falls
    back to synthetic detections when no weights are present).
    """

    def __init__(self, camera_id: int, source: Optional[str | int] = None, backend_url: str = BACKEND_BASE_URL):
        self.camera_id = camera_id
        self.source = source
        self.detector = Detector()
        self.tracker = ByteTrackWrapper()
        self.rule_engine = RuleEngine(camera_id, backend_url=backend_url)

    def run(self, max_frames: Optional[int] = None, frame_interval: float = 1.0):
        frame = None
        cap = None
        if self.source is not None:
            import cv2

            cap = cv2.VideoCapture(self.source)

        count = 0
        try:
            while max_frames is None or count < max_frames:
                if cap is not None:
                    ok, frame = cap.read()
                    if not ok:
                        break

                frame_result = self.detector.detect(frame)
                frame_result = self.tracker.update(frame_result)
                self.rule_engine.process(frame_result)

                count += 1
                time.sleep(frame_interval)
        finally:
            if cap is not None:
                cap.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ForgeGuard AI safety pipeline for one camera.")
    parser.add_argument("--camera-id", type=int, required=True)
    parser.add_argument("--source", type=str, default=None, help="Webcam index, RTSP URL, or video file. Omit for DEMO mode.")
    parser.add_argument("--backend-url", type=str, default=BACKEND_BASE_URL)
    parser.add_argument("--frame-interval", type=float, default=1.0)
    args = parser.parse_args()

    source: Optional[str | int] = args.source
    if source is not None and source.isdigit():
        source = int(source)

    worker = CameraWorker(camera_id=args.camera_id, source=source, backend_url=args.backend_url)
    worker.run(frame_interval=args.frame_interval)
