import os
from pathlib import Path
from ultralytics import YOLO

def train():
    dataset_yaml = Path(__file__).parent / "final" / "data.yaml"
    if not dataset_yaml.exists():
        print(f"Error: Dataset yaml not found at {dataset_yaml}")
        return

    print("=" * 60)
    print(f"Starting YOLO Training on FINAL MERGED Dataset")
    print(f"Dataset path: {dataset_yaml}")
    print("=" * 60)

    # Let's use the best model we have or fallback to yolov8n
    base_dir = Path(__file__).parent
    model_type = str(base_dir / "best.pt")
    if not Path(model_type).exists():
        model_type = "yolov8n.pt"
        
    model = YOLO(model_type)

    epochs = 10
    imgsz = 640
    batch = 16

    print(f"Training parameters: model={model_type}, epochs={epochs}, imgsz={imgsz}, batch={batch}")
    
    results = model.train(
        data=str(dataset_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name="yolo_final_merged",
        project="runs/detect",
        exist_ok=True
    )

    print("=" * 60)
    print("Training Completed Successfully!")
    print(f"Best model saved at: {results.save_dir}/weights/best.pt")
    print("=" * 60)

if __name__ == "__main__":
    train()
