# ForeguardAI 🛡️ — AI Industrial Safety & Violation Evidence System

**ForeguardAI** is a real-time computer vision system built with YOLOv8 and Flask to monitor workplace safety compliance, detect Personal Protective Equipment (PPE), identify safety violations, and automatically generate snapshot evidence logs.

---

## 🌟 Key Features

- 🛡️ **19-Class Multi-Object Detection**: Detects workers, safety gear (helmets, vests, masks, gloves, boots, glasses, earmuffs, uniforms), machinery, tools, and violations simultaneously.
- 🚨 **Real-Time Violation Alerts**: Instant alerts for `No helmet`, `No safety vest`, `No mask`, `smoking`, and `Mobile phone` usage.
- 📸 **Automated Snapshot Evidence Logging**: Saves high-resolution annotated evidence snapshots with metadata (timestamps, confidence score, violation type, source camera).
- 🌐 **Interactive Web Dashboard**: Built with Flask and modern Glassmorphism Dark UI (`http://localhost:5000`) for live streaming, alert feeds, confidence threshold tuning, and CSV report export.

---

## 📋 19 Detected Classes

| ID | Class Name | Category |
| :--- | :--- | :--- |
| 0 | Person | Personnel |
| 1 | Helmet | Safety Gear |
| 2 | No helmet | 🚨 Violation (Critical) |
| 3 | Gloves | Safety Gear |
| 4 | No gloves | 🚨 Violation |
| 5 | Boots | Safety Gear |
| 6 | No boots | 🚨 Violation |
| 7 | Glasses | Safety Gear |
| 8 | No glasses | 🚨 Violation |
| 9 | Safety vest | Safety Gear |
| 10 | No safety | 🚨 Violation (Critical) |
| 11 | Face mask | Safety Gear |
| 12 | Face shield | Safety Gear |
| 13 | Mobile phone | 🚨 Violation (Distraction) |
| 14 | Tools | Worksite Assets |
| 15 | Machine | Industrial Machinery |
| 16 | Machine guard | Safety Equipment |
| 17 | Earmuffs | Safety Gear |
| 18 | Uniform | Workwear |

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install ultralytics flask opencv-python numpy
```

### 2. Run the Web Dashboard
```bash
python web_app.py
```
Open your browser at **`http://localhost:5000`**.

### 3. Run Desktop Camera OpenCV Window
```bash
python run_laptop_camera.py
```

---

## 📊 Training Performance Summary

- **Total Epochs**: 10 Epochs Trained
- **Final Model Accuracy (mAP50)**: **62.6%**
- **Precision Peak**: **72.4%**
- **Model File**: `best.pt`
