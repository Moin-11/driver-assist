from ultralytics import YOLO

# 1. Load the model you trained on Colab
# CRITICAL: We load the local file you downloaded.
TRAINED_MODEL = 'best.pt' 

# 2. Specify the source data for prediction
SOURCE_VIDEO = 'traffic-sign-to-test.mp4'

# 3. Explicitly set the device to 'cpu'
DEVICE = 'cpu'

# Load the trained model weights
model = YOLO(TRAINED_MODEL)

print(f"Starting inference on {SOURCE_VIDEO} using {DEVICE}...")

# Run prediction
results = model.predict(
    source=SOURCE_VIDEO,
    conf=0.5,           # Confidence threshold (e.g., only show detections > 50% confidence)
    device=DEVICE,
    save=True           # Save the resulting video with boxes and labels
)

print("\n✅ Inference complete! Check the 'runs/detect/' folder for the output video.")