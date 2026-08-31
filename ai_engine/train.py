from ultralytics import YOLO

# 1. Load a pre-trained YOLOv8 model (nano version is fastest for testing)
model = YOLO('yolov8n.pt')

# 2. Train the model on your dataset
# We point to your data.yaml file and tell it to train for 50 epochs.
results = model.train(
    data='./final/data.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    project='forgeguard_training',
    name='run1'
)

print("Training complete! Your trained weights are saved in: forgeguard_training/run1/weights/best.pt")
