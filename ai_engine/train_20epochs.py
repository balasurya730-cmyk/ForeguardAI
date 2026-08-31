from ultralytics import YOLO
from pathlib import Path

def train_fine_tune():
    weights_path = Path("E:/tcs/dataset/best.pt")
    if not weights_path.exists():
        print(f"Error: Could not find best.pt at {weights_path}")
        return

    print("=" * 60)
    print("Fine-tuning YOLO Model from 10-epoch best.pt for 10 Additional Epochs...")
    print("=" * 60)

    model = YOLO(str(weights_path))
    
    # Train fine-tuning for 10 additional epochs
    results = model.train(
        data="E:/tcs/dataset/final/data.yaml",
        epochs=10,
        imgsz=640,
        batch=16,
        name="yolo_final_extended",
        project="runs/detect/runs/detect",
        exist_ok=True
    )

if __name__ == "__main__":
    train_fine_tune()
