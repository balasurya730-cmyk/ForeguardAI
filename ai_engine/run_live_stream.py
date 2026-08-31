import cv2
import requests
import base64
import threading
import time
from flask import Flask, Response
from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

model = YOLO('best.pt')
API_URL = "http://127.0.0.1:8001/api/safety/events"

CLASS_MAP = {
    0: "PERSON", 1: "HELMET", 2: "NO_HELMET", 3: "GLOVES", 4: "NO_GLOVES",
    5: "BOOTS", 6: "NO_BOOTS", 7: "GLASSES", 8: "NO_GLASSES", 9: "SAFETY_VEST",
    10: "NO_SAFETY_VEST", 11: "FACE_MASK", 12: "FACE_SHIELD", 13: "MOBILE_PHONE",
    14: "TOOLS", 15: "MACHINE", 16: "MACHINE_GUARD", 17: "EARMUFFS", 18: "UNIFORM"
}

HAZARD_CLASSES = {
    "NO_HELMET", "NO_GLOVES", "NO_BOOTS", "NO_GLASSES", "NO_SAFETY_VEST", "MOBILE_PHONE", "FACE_MASK"
}

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Global variables for threading
latest_frame = None
output_frame = None
frame_lock = threading.Lock()
ai_detection_enabled = True

# Thread 1: Constantly read the camera as fast as possible to prevent buffer lag
def camera_reader():
    global latest_frame
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                latest_frame = frame.copy()
        else:
            time.sleep(0.01)

# Thread 2: Run AI inference only on the freshest frame
def process_camera():
    global latest_frame, output_frame
    cooldown = 0
    
    while True:
        with frame_lock:
            if latest_frame is None:
                frame_to_process = None
            else:
                frame_to_process = latest_frame.copy()
                
        if frame_to_process is None:
            time.sleep(0.05)
            continue
            
        if not ai_detection_enabled:
            with frame_lock:
                output_frame = frame_to_process.copy()
            time.sleep(0.03)
            continue

        # Run AI inference with an ultra-low global threshold, then filter specific classes in python
        results = model(frame_to_process, stream=True, conf=0.02)

        for r in results:
            boxes = r.boxes
            detected_types = []
            persons = []
            all_detections = []
            
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                violation_type = CLASS_MAP.get(class_id, "UNKNOWN")
                
                # Class-specific confidence filtering
                if violation_type == "MOBILE_PHONE":
                    if confidence < 0.05: # Extremely sensitive for mobile phones
                        continue
                else:
                    if confidence < 0.15: # Standard sensitivity for everything else
                        continue
                        
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                detected_types.append(violation_type)
                all_detections.append({"violation_type": violation_type, "confidence": confidence, "coords": (x1, y1, x2, y2)})
                
                if violation_type == "PERSON":
                    persons.append((x1, y1, x2, y2, confidence))
            
            # Smart Heuristic Fallback
            for (px1, py1, px2, py2, pconf) in persons:
                if "HELMET" not in detected_types and "NO_HELMET" not in detected_types:
                    hx1, hy1, hx2, hy2 = px1, max(0, py1 - int((py2 - py1) * 0.1)), px2, py1 + int((py2 - py1) * 0.15)
                    all_detections.append({
                        "violation_type": "NO_HELMET", "confidence": pconf * 0.9, "coords": (hx1, hy1, hx2, hy2)
                    })
                if "FACE_MASK" not in detected_types:
                    mx1, my1, mx2, my2 = px1 + int((px2-px1)*0.2), py1 + int((py2-py1)*0.15), px2 - int((px2-px1)*0.2), py1 + int((py2-py1)*0.3)
                    all_detections.append({
                        "violation_type": "FACE_MASK", "confidence": pconf * 0.9, "coords": (mx1, my1, mx2, my2)
                    })
                    
            for det in all_detections:
                violation_type = det["violation_type"]
                confidence = det["confidence"]
                x1, y1, x2, y2 = det["coords"]
                
                color = (255, 0, 0)
                if violation_type in HAZARD_CLASSES:
                    color = (0, 0, 255)
                elif "NO_" not in violation_type and violation_type not in ["PERSON", "MACHINE", "TOOLS", "UNIFORM"]:
                    color = (0, 255, 0)
                else:
                    color = (150, 150, 150)
                
                cv2.rectangle(frame_to_process, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame_to_process, f"{violation_type} ({confidence:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Dynamic threshold for dashboard alerts
                alert_threshold = 0.05 if violation_type == "MOBILE_PHONE" else 0.20
                if violation_type in HAZARD_CLASSES and confidence >= alert_threshold:
                    if cooldown <= 0:
                        _, buffer = cv2.imencode('.jpg', frame_to_process)
                        img_base64 = base64.b64encode(buffer).decode('utf-8')
                        evidence_data = f"data:image/jpeg;base64,{img_base64}"
                        
                        payload = {
                            "camera_id": 1, "violation_type": violation_type,
                            "confidence": confidence, "duration_seconds": 1.0,
                            "evidence_path": evidence_data
                        }
                        try:
                            requests.post(API_URL, json=payload)
                        except Exception:
                            pass
                        cooldown = 15 # Shorter cooldown due to higher FPS
                    else:
                        cooldown -= 1

        with frame_lock:
            output_frame = frame_to_process.copy()

def generate():
    global output_frame
    while True:
        with frame_lock:
            if output_frame is None:
                frame_to_yield = None
            else:
                frame_to_yield = output_frame.copy()
                
        if frame_to_yield is None:
            time.sleep(0.05)
            continue
            
        ret, encoded_image = cv2.imencode(".jpg", frame_to_yield)
        if ret:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')
        
        time.sleep(0.03) # Cap stream at ~30fps

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/api/toggle_detection", methods=["POST"])
def toggle_detection():
    global ai_detection_enabled
    ai_detection_enabled = not ai_detection_enabled
    return {"status": "success", "ai_enabled": ai_detection_enabled}

@app.route("/api/detection_status", methods=["GET"])
def detection_status():
    global ai_detection_enabled
    return {"ai_enabled": ai_detection_enabled}

if __name__ == '__main__':
    # Start high-speed camera reader thread to eliminate lag
    reader_thread = threading.Thread(target=camera_reader)
    reader_thread.daemon = True
    reader_thread.start()
    
    # Start AI processing thread
    ai_thread = threading.Thread(target=process_camera)
    ai_thread.daemon = True
    ai_thread.start()
    
    print("Zero-Latency AI Streaming on http://127.0.0.1:8002/video_feed")
    app.run(host="0.0.0.0", port=8002, debug=False, use_reloader=False)
