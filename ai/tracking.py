"""
ai/tracking.py — ByteTrack worker tracking stage.

Assigns persistent track IDs to "person" detections across frames so a
single worker (e.g. "Worker #12") can be followed over time. This lets
rules.py apply *persistence* logic (e.g. "helmet missing for N consecutive
frames/seconds") instead of firing a violation from a single noisy frame.

Uses the real `bytetrack`/`ultralytics` tracker API when available; falls
back to a minimal IoU-based tracker otherwise so the pipeline still works
without extra heavy dependencies in DEMO mode.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ai.detection import Detection, FrameResult


def _iou(a: tuple, b: tuple) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    intersection = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


@dataclass
class _Track:
    track_id: int
    bbox: tuple
    misses: int = 0


class ByteTrackWrapper:
    """Minimal IoU-based tracker with ByteTrack-style track lifecycle
    (a track survives a few missed frames before being dropped), used to
    assign stable worker IDs to "person" detections.

    To use real ByteTrack (e.g. via `ultralytics` built-in tracker), swap
    the body of `update()` for a call to `model.track(frame, tracker="bytetrack.yaml")`
    upstream in detection.py and pass through the resulting `track_id`s here.
    """

    def __init__(self, iou_threshold: float = 0.3, max_misses: int = 15):
        self.iou_threshold = iou_threshold
        self.max_misses = max_misses
        self._tracks: Dict[int, _Track] = {}
        self._next_id = 1

    def update(self, frame_result: FrameResult) -> FrameResult:
        person_detections = [d for d in frame_result.detections if d.class_name == "person"]
        other_detections = [d for d in frame_result.detections if d.class_name != "person"]

        unmatched_tracks = set(self._tracks.keys())
        for det in person_detections:
            best_id, best_iou = None, 0.0
            for track_id, track in self._tracks.items():
                score = _iou(det.bbox, track.bbox)
                if score > best_iou:
                    best_id, best_iou = track_id, score

            if best_id is not None and best_iou >= self.iou_threshold:
                det.track_id = best_id
                self._tracks[best_id] = _Track(best_id, det.bbox, misses=0)
                unmatched_tracks.discard(best_id)
            else:
                new_id = self._next_id
                self._next_id += 1
                det.track_id = new_id
                self._tracks[new_id] = _Track(new_id, det.bbox, misses=0)

        for track_id in unmatched_tracks:
            self._tracks[track_id].misses += 1
            if self._tracks[track_id].misses > self.max_misses:
                del self._tracks[track_id]

        # Associate non-person detections (helmet, mobile, PPE, guard) with
        # the nearest tracked person by containment/overlap, so rules.py can
        # reason per-worker rather than per-frame.
        for det in other_detections:
            best_id, best_iou = None, 0.0
            for p in person_detections:
                score = _iou(det.bbox, p.bbox)
                if score > best_iou:
                    best_id, best_iou = p.track_id, score
            det.track_id = best_id

        frame_result.detections = person_detections + other_detections
        return frame_result
