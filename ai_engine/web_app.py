import os
import cv2
import json
import time
import datetime
import numpy as np
from pathlib import Path
from flask import Flask, render_template, Response, jsonify, request, send_from_directory

app = Flask(__name__)

# Base Directories
BASE_DIR = Path(__file__).parent
EVIDENCE_DIR = BASE_DIR / "static" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_JSON = BASE_DIR / "evidence_log.json"

# List of target classes
TARGET_CLASSES = [
    "Person", "Helmet", "No helmet", "Gloves", "No gloves",
    "Boots", "No boots", "Glasses", "No glasses", "Safety vest",
    "No safety", "Face mask", "Face shield", "Mobile phone",
    "Tools", "Machine", "Machine guard", "Earmuffs", "Uniform"
]

# Violations and their severity mapping
VIOLATION_RULES = {
    "No helmet": {"severity": "CRITICAL", "desc": "Worker without hardhat/helmet detected!", "color": "#ff4757"},
    "NO-Hardhat": {"severity": "CRITICAL", "desc": "Worker without hardhat/helmet detected!", "color": "#ff4757"},
    "NO-Mask": {"severity": "MEDIUM", "desc": "Worker without face mask detected!", "color": "#ffa502"},
    "No safety": {"severity": "CRITICAL", "desc": "Worker without safety vest detected!", "color": "#ff4757"},
    "NO-Safety Vest": {"severity": "CRITICAL", "desc": "Worker without safety vest detected!", "color": "#ff4757"},
    "smoking": {"severity": "CRITICAL", "desc": "Unlawful smoking in hazardous workplace zone!", "color": "#ff4757"},
    "Mobile phone": {"severity": "HIGH", "desc": "Distracted worker operating mobile phone near equipment!", "color": "#ff7f50"},
    "phone": {"severity": "HIGH", "desc": "Distracted worker operating mobile phone near equipment!", "color": "#ff7f50"}
}

# Global State
app_state = {
    "camera_index": 0,
    "conf_thresh": 0.25,
    "sound_alerts": True,
    "active_model_path": "Loading...",
    "model": None,
    "last_snapshot_time": {},  # Cooldown per violation type
    "cooldown_seconds": 4.0,
    "total_scans": 0,
    "total_violations": 0
}

# Load or initialize evidence logs
def load_evidence_logs():
    if EVIDENCE_JSON.exists():
        try:
            with open(EVIDENCE_JSON, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading evidence JSON: {e}")
            return []
    return []

def save_evidence_logs(logs):
    with open(EVIDENCE_JSON, "w") as f:
        json.dump(logs, f, indent=2)

evidence_logs = load_evidence_logs()

# Model Finder
def load_yolo_model():
    candidate_paths = [
        BASE_DIR / "runs" / "detect" / "runs" / "detect" / "yolo_final_merged" / "weights" / "best.pt",
        BASE_DIR / "runs" / "detect" / "yolo_final_merged" / "weights" / "best.pt",
        BASE_DIR / "best.pt",
        BASE_DIR / "1st" / "best.pt",
        BASE_DIR / "yolov8n.pt"
    ]
    
    selected_path = None
    for path in candidate_paths:
        if path.exists():
            selected_path = path
            break
            
    if selected_path is None:
        selected_path = "yolov8n.pt"

    app_state["active_model_path"] = str(selected_path)
    print(f"Flask App Loading Model from: {selected_path}")
    
    try:
        from ultralytics import YOLO
        model = YOLO(str(selected_path))
        return model
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return None

# Video Stream Generator
def generate_frames():
    model = load_yolo_model()
    app_state["model"] = model
    
    cap = cv2.VideoCapture(app_state["camera_index"], cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(app_state["camera_index"])
        
    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(100, 3), dtype="uint8").tolist()
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            # Generate a synthetic frame if webcam is busy or unavailable
            frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.putText(frame, "Webcam Offline / In Use", (350, 360),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            cv2.putText(frame, "Connect camera or check permissions", (380, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
            time.sleep(0.1)
        
        frame_count += 1
        app_state["total_scans"] += 1
        conf_t = app_state["conf_thresh"]
        
        annotated_frame = frame.copy()
        current_time = time.time()
        
        if model is not None and ret:
            try:
                results = model.predict(source=frame, conf=conf_t, verbose=False)
                if len(results) > 0:
                    boxes = results[0].boxes
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        cls_id = int(box.cls[0])
                        
                        raw_name = model.names[cls_id] if hasattr(model, 'names') and cls_id in model.names else f"Class_{cls_id}"
                        
                        # Match label
                        label_name = raw_name
                        for target in TARGET_CLASSES:
                            if target.lower() in raw_name.lower() or raw_name.lower() in target.lower():
                                label_name = target
                                break
                        
                        # Check violation
                        is_violation = False
                        violation_info = None
                        for key, rule in VIOLATION_RULES.items():
                            if key.lower() in label_name.lower():
                                is_violation = True
                                violation_info = rule
                                break
                        
                        if is_violation:
                            box_color = (0, 0, 255) # Red for violation
                        else:
                            box_color = (0, 255, 100) # Green for compliant
                            
                        # Draw bounding box
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)
                        
                        # Label Banner
                        tag_text = f"{label_name} {conf*100:.0f}%"
                        (tw, th), _ = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        cv2.rectangle(annotated_frame, (x1, max(0, y1 - th - 10)), (x1 + tw + 10, y1), box_color, -1)
                        cv2.putText(annotated_frame, tag_text, (x1 + 5, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
                        
                        # Trigger Evidence Capture if Violation
                        if is_violation and violation_info:
                            last_t = app_state["last_snapshot_time"].get(label_name, 0)
                            if current_time - last_t >= app_state["cooldown_seconds"]:
                                app_state["last_snapshot_time"][label_name] = current_time
                                app_state["total_violations"] += 1
                                
                                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                snap_filename = f"evidence_{file_timestamp}_{cls_id}.jpg"
                                snap_path = EVIDENCE_DIR / snap_filename
                                
                                cv2.imwrite(str(snap_path), annotated_frame)
                                
                                new_entry = {
                                    "id": int(time.time() * 1000),
                                    "violation": label_name,
                                    "severity": violation_info["severity"],
                                    "desc": violation_info["desc"],
                                    "color": violation_info["color"],
                                    "confidence": round(conf * 100, 1),
                                    "timestamp": timestamp_str,
                                    "image": f"/static/evidence/{snap_filename}",
                                    "camera": f"Cam #{app_state['camera_index']} (Main Entrance)",
                                    "bbox": [x1, y1, x2, y2]
                                }
                                
                                evidence_logs.insert(0, new_entry)
                                if len(evidence_logs) > 100:
                                    evidence_logs.pop()
                                save_evidence_logs(evidence_logs)
            except Exception as ex:
                print(f"Inference frame error: {ex}")
                
        # Encode Frame to JPG
        ret_jpeg, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    total_viols = len(evidence_logs)
    critical_cnt = sum(1 for e in evidence_logs if e.get("severity") == "CRITICAL")
    high_cnt = sum(1 for e in evidence_logs if e.get("severity") == "HIGH")
    medium_cnt = sum(1 for e in evidence_logs if e.get("severity") == "MEDIUM")
    
    # Calculate safety compliance score
    total_scans = max(100, app_state["total_scans"])
    compliance_score = max(60.0, round(100.0 - (total_viols * 1.5), 1))
    
    breakdown = {}
    for e in evidence_logs:
        v = e.get("violation", "Unknown")
        breakdown[v] = breakdown.get(v, 0) + 1
        
    return jsonify({
        "total_scans": app_state["total_scans"],
        "total_violations": total_viols,
        "critical_violations": critical_cnt,
        "high_violations": high_cnt,
        "medium_violations": medium_cnt,
        "compliance_score": compliance_score,
        "active_model": app_state["active_model_path"],
        "conf_threshold": app_state["conf_thresh"],
        "target_classes": TARGET_CLASSES,
        "breakdown": breakdown
    })

@app.route('/api/evidence')
def get_evidence():
    violation_filter = request.args.get('violation', 'all')
    severity_filter = request.args.get('severity', 'all')
    
    filtered = evidence_logs
    if violation_filter != 'all':
        filtered = [e for e in filtered if e.get("violation") == violation_filter]
    if severity_filter != 'all':
        filtered = [e for e in filtered if e.get("severity") == severity_filter]
        
    return jsonify(filtered)

@app.route('/api/evidence/delete/<int:item_id>', methods=['DELETE'])
def delete_evidence(item_id):
    global evidence_logs
    evidence_logs = [e for e in evidence_logs if e.get("id") != item_id]
    save_evidence_logs(evidence_logs)
    return jsonify({"status": "success", "message": f"Evidence {item_id} deleted."})

@app.route('/api/evidence/clear', methods=['POST'])
def clear_all_evidence():
    global evidence_logs
    evidence_logs = []
    save_evidence_logs(evidence_logs)
    return jsonify({"status": "success", "message": "All evidence logs cleared."})

@app.route('/api/trigger_snapshot', methods=['POST'])
def trigger_snapshot():
    # Force snapshot manual capture
    cap = cv2.VideoCapture(app_state["camera_index"])
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        snap_name = f"manual_{file_ts}.jpg"
        snap_path = EVIDENCE_DIR / snap_name
        cv2.imwrite(str(snap_path), frame)
        
        entry = {
            "id": int(time.time() * 1000),
            "violation": "Manual Snapshot",
            "severity": "MEDIUM",
            "desc": "Manual evidence capture by security officer.",
            "color": "#00f2fe",
            "confidence": 100.0,
            "timestamp": timestamp_str,
            "image": f"/static/evidence/{snap_name}",
            "camera": f"Cam #{app_state['camera_index']} (Manual)",
            "bbox": []
        }
        evidence_logs.insert(0, entry)
        save_evidence_logs(evidence_logs)
        return jsonify({"status": "success", "entry": entry})
    return jsonify({"status": "error", "message": "Could not capture frame from webcam."}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json or {}
    if "conf_thresh" in data:
        app_state["conf_thresh"] = float(data["conf_thresh"])
    if "sound_alerts" in data:
        app_state["sound_alerts"] = bool(data["sound_alerts"])
    if "camera_index" in data:
        app_state["camera_index"] = int(data["camera_index"])
    return jsonify({"status": "success", "settings": {
        "conf_thresh": app_state["conf_thresh"],
        "sound_alerts": app_state["sound_alerts"],
        "camera_index": app_state["camera_index"]
    }})

if __name__ == '__main__':
    print("="*70)
    print("  Starting AI Safety Monitoring & Violation Evidence Web Server")
    print("  Open in Browser: http://127.0.0.1:5000")
    print("="*70)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
