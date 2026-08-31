import cv2
import requests
import base64
from ultralytics import YOLO

# 1. Load your trained model
model = YOLO('best.pt')

# 2. ForgeGuard API Endpoint
API_URL = "http://127.0.0.1:8001/api/safety/events"

# 3. Exact 19-class mapping to the ForgeGuard Dashboard
CLASS_MAP = {
    0: "PERSON",
    1: "HELMET",
    2: "NO_HELMET",
    3: "GLOVES",
    4: "NO_GLOVES",
    5: "BOOTS",
    6: "NO_BOOTS",
    7: "GLASSES",
    8: "NO_GLASSES",
    9: "SAFETY_VEST",
    10: "NO_SAFETY_VEST",
    11: "FACE_MASK",
    12: "FACE_SHIELD",
    13: "MOBILE_PHONE",
    14: "TOOLS",
    15: "MACHINE",
    16: "MACHINE_GUARD",
    17: "EARMUFFS",
    18: "UNIFORM"
}

# Define which classes we actually want to trigger alerts for in the dashboard
# (We don't need to send an alert every time we see a Person or a Machine, just the hazards)
HAZARD_CLASSES = {
    "NO_HELMET", "NO_GLOVES", "NO_BOOTS", "NO_GLASSES", "NO_SAFETY_VEST", "MOBILE_PHONE"
}

# 4. Open Webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run AI inference
    results = model(frame, stream=True)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            violation_type = CLASS_MAP.get(class_id)
            
            # If it's one of our defined hazard classes and we're at least 60% confident
            if violation_type in HAZARD_CLASSES and confidence > 0.60:
                
                # Draw bounding box on the frame
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"{violation_type} ({confidence:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # Convert frame to Base64 for evidence
                _, buffer = cv2.imencode('.jpg', frame)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                evidence_data = f"data:image/jpeg;base64,{img_base64}"

                # Send to Web Dashboard
                payload = {
                    "camera_id": 1,
                    "violation_type": violation_type,
                    "confidence": confidence,
                    "duration_seconds": 1.0,
                    "evidence_path": evidence_data
                }
                
                try:
                    res = requests.post(API_URL, json=payload)
                    print(f"Sent {violation_type} to Dashboard! (Status: {res.status_code})")
                except Exception as e:
                    pass

    # Display video feed locally
    cv2.imshow("ForgeGuard 19-Class AI Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
