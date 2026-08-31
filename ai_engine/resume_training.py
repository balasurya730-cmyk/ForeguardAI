from ultralytics import YOLO
from pathlib import Path

def resume_train():
    weights_path = Path("E:/tcs/dataset/runs/detect/runs/detect/yolo_final_merged/weights/last.pt")
    if not weights_path.exists():
        print(f"Error: Could not find last.pt at {weights_path}")
        return

    print("=" * 60)
    print("Resuming YOLO Training from last.pt...")
    print("=" * 60)

    model = YOLO(str(weights_path))
    
    # Resume training
    results = model.train(resume=True)

if __name__ == "__main__":
    resume_train()
