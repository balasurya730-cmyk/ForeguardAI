import cv2
import time
from pathlib import Path
from ultralytics import YOLO
import numpy as np

def demo_multi_object_detection():
    base_dir = Path("E:/tcs/dataset")
    model_path = base_dir / "best.pt"

    print("=" * 70)
    print("  YOLO Multi-Object Simultaneous Detection Test")
    print("=" * 70)

    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        return

    model = YOLO(str(model_path))

    # Read webcam frame or sample image
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not available, testing model capabilities...")
        return

    for _ in range(10):
        ret, frame = cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("Could not grab camera frame.")
        return

    # Run inference with NMS (Non-Maximum Suppression) to detect ALL objects at once
    results = model.predict(source=frame, conf=0.25, verbose=False)

    annotated = frame.copy()
    detections_summary = []

    if len(results) > 0:
        boxes = results[0].boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = model.names.get(cls_id, f"Class {cls_id}")

            detections_summary.append(f"{cls_name} ({conf*100:.0f}%)")

            # Draw box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 242, 254), 2)
            cv2.putText(annotated, f"{cls_name} {conf*100:.0f}%", (x1 + 5, max(15, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2)

    out_file = base_dir / "multi_detection_test.jpg"
    cv2.imwrite(str(out_file), annotated)

    print(f"\nSuccessfully detected {len(detections_summary)} objects in ONE SINGLE frame:")
    for item in detections_summary:
        print(f"  -> {item}")

if __name__ == "__main__":
    demo_multi_object_detection()
