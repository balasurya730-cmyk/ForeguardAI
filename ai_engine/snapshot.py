import cv2
import sys
from pathlib import Path
from ultralytics import YOLO
import numpy as np

def take_snapshot(model_path):
    base_dir = Path(__file__).parent
    
    print(f"Loading Model Weights: {model_path}")
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    num_classes = len(model.names) if hasattr(model, 'names') else 80
    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(max(80, num_classes), 3), dtype="uint8").tolist()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print(f"Error: Camera could not be opened!")
        return

    # Read a few frames to let the camera auto-adjust brightness
    for _ in range(10):
        ret, frame = cap.read()

    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return

    # Run inference
    results = model.predict(source=frame, conf=0.35, verbose=False)
    annotated_frame = frame.copy()
    
    if len(results) > 0:
        boxes = results[0].boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])

            label_name = model.names[cls_id] if hasattr(model, 'names') else f"Class {cls_id}"
            color = colors[cls_id % len(colors)]

            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            caption = f"{label_name} {conf:.2f}"
            (w, h), _ = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated_frame, (x1, y1 - h - 10), (x1 + w + 10, y1), color, -1)
            cv2.putText(annotated_frame, caption, (x1 + 5, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    out_path = str(base_dir / "epoch1_snapshot.jpg")
    cv2.imwrite(out_path, annotated_frame)
    print(f"Snapshot saved to {out_path}")
    
    cap.release()

if __name__ == "__main__":
    weights = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "best.pt")
    take_snapshot(weights)
