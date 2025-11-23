from ultralytics import YOLO

# --- Configuration ---
# Your configuration file created in Step 0
DATASET_CONFIG = 'data.yaml' 

# YOLOv12n model size (Nano - fast and efficient)
MODEL_NAME = 'yolo12n.pt' 

# Output directory name for this run
PROJECT_NAME = 'traffic_sign_yolov12n' 

# --- Training Parameters ---
# Adjust these based on your dataset size and hardware
EPOCHS = 50 
IMAGE_SIZE = 640
BATCH_SIZE = 16 # Reduce this if you run out of GPU memory
DEVICE = 'cpu' # Use GPU 0. Change to 'cpu' if you don't have a GPU.

print(f"Loading model: {MODEL_NAME}")
# Load a pre-trained YOLOv12n model
model = YOLO(MODEL_NAME)

print(f"Starting training for {EPOCHS} epochs...")
# Start training
results = model.train(
    data=DATASET_CONFIG, 
    epochs=EPOCHS, 
    imgsz=IMAGE_SIZE, 
    batch=BATCH_SIZE,
    name=PROJECT_NAME,
    device=DEVICE,
    # Optional: set a unique seed for reproducibility
    seed=42 
)

print("\n✅ Training complete!")
# Your trained weights will be saved in: runs/detect/traffic_sign_yolov12n/weights/best.pt