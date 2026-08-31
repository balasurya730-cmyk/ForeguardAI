import json
from pathlib import Path
from ultralytics import YOLO

def check_all_classes():
    best_model_path = Path("E:/tcs/dataset/best.pt")
    data_yaml_path = Path("E:/tcs/dataset/final/data.yaml")

    print("=" * 70)
    print("  DIAGNOSTIC TEST: Verifying Detection Capabilities for All 19 Classes")
    print("=" * 70)

    if not best_model_path.exists():
        print(f"Error: Could not find model at {best_model_path}")
        return

    model = YOLO(str(best_model_path))

    print("\n1. Model Class Names List (Total: {} classes):".format(len(model.names)))
    for idx, name in model.names.items():
        print(f"   Class ID {idx:2d} -> {name}")

    print("\n2. Running Validation Evaluation on Test/Val Dataset...")
    try:
        metrics = model.val(data=str(data_yaml_path), verbose=True)
        print("\n" + "=" * 70)
        print("  CLASS PERFORMANCE BREAKDOWN:")
        print("=" * 70)
        
        # Check per-class mAP50 scores
        if hasattr(metrics, 'maps') and metrics.maps is not None:
            for idx, map50 in enumerate(metrics.maps):
                cls_name = model.names.get(idx, f"Class {idx}")
                status = "DETECTED & TRAINED ✅" if map50 > 0.05 else "NEEDS MORE TRAINING DATA ⚠️"
                print(f"  [{idx:2d}] {cls_name:<20}: mAP50 = {map50*100:5.1f}% | {status}")
                
        print("\nOverall Model mAP50 Accuracy: {:.1f}%".format(metrics.box.map50 * 100))
        print("Overall Model Precision: {:.1f}%".format(metrics.box.mp * 100))
        print("Overall Model Recall: {:.1f}%".format(metrics.box.mr * 100))
        
    except Exception as e:
        print(f"Validation error: {e}")

if __name__ == "__main__":
    check_all_classes()
