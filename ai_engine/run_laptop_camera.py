import cv2
import time
import sys
from pathlib import Path
from ultralytics import YOLO
import numpy as np

def run_webcam(model_path=None, camera_index=0, conf_thresh=0.25):
    base_dir = Path(__file__).parent
    
    if model_path is None or not Path(model_path).exists():
        candidate_paths = [
            base_dir / "best.pt",
            base_dir / "runs" / "detect" / "runs" / "detect" / "yolo_final_merged" / "weights" / "best.pt",
            base_dir / "1st" / "best.pt",
            base_dir / "yolov8n.pt"
        ]
        for p in candidate_paths:
            if p.exists():
                model_path = str(p)
                break
                
    if model_path is None or not Path(model_path).exists():
        model_path = "yolov8n.pt"

    print("=" * 60)
    print(f"YOLO Real-Time Laptop Camera System")
    print(f"Loading Model Weights: {model_path}")
    print("=" * 60)

    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error loading model {model_path}: {e}")
        return

    num_classes = len(model.names) if hasattr(model, 'names') else 80
    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(max(80, num_classes), 3), dtype="uint8").tolist()

    # Open Camera with fallback
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened() or not cap.read()[0]:
        cap.release()
        cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"\n[ERROR] Laptop Camera (Index {camera_index}) could not be opened!")
        print("Reason: Another program (like Zoom, Teams, Web App) may be using your camera.")
        print("Please close any active camera apps and try again.\n")
        return

    print("\n[SUCCESS] Laptop Camera opened successfully!")
    print("Controls: Press 'q' or 'ESC' to exit window. Press '+' or '-' to adjust confidence.\n")

    window_name = "YOLO AI Laptop Camera Feed (Press Q to Quit)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1024, 768)

    prev_time = time.time()
    fps = 0.0

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.05)
            continue

        results = model.predict(source=frame, conf=conf_thresh, verbose=False)
        annotated_frame = frame.copy()
        
        if len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])

                label_name = model.names[cls_id] if hasattr(model, 'names') and cls_id in model.names else f"Class {cls_id}"
                color = colors[cls_id % len(colors)]

                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                caption = f"{label_name} {conf:.2f}"
                (w, h), _ = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(annotated_frame, (x1, max(0, y1 - h - 10)), (x1 + w + 10, y1), color, -1)
                cv2.putText(annotated_frame, caption, (x1 + 5, max(12, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        curr_time = time.time()
        fps = 0.9 * fps + 0.1 * (1.0 / (curr_time - prev_time + 1e-6))
        prev_time = curr_time

        hud_text = f"FPS: {fps:.1f} | Conf: {conf_thresh:.2f} | Objects: {len(results[0].boxes)}"
        cv2.rectangle(annotated_frame, (0, 0), (annotated_frame.shape[1], 40), (20, 20, 20), -1)
        cv2.putText(annotated_frame, hud_text, (15, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 200), 2, cv2.LINE_AA)

        cv2.imshow(window_name, annotated_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('+') or key == ord('='):
            conf_thresh = min(0.95, conf_thresh + 0.05)
        elif key == ord('-'):
            conf_thresh = max(0.05, conf_thresh - 0.05)

    cap.release()
    cv2.destroyAllWindows()
    print("Laptop Camera feed stopped cleanly.")

if __name__ == "__main__":
    weights = sys.argv[1] if len(sys.argv) > 1 else None
    run_webcam(model_path=weights)
