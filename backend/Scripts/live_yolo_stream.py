import cv2
import sys
import time
import numpy as np

# --- YOLO/Ultralytics Import ---
try:
    from ultralytics import YOLO
except ImportError:
    print("❌ ERROR: Ultralytics YOLO library not found. Please install it (pip install ultralytics).")
    sys.exit()

# --- Camera Import-Safety (Picamera2 for RPi/Linux) ---
try:
    from picamera2 import Picamera2    # type: ignore
    PICAMERA2_AVAILABLE = True
except Exception:
    PICAMERA2_AVAILABLE = False
    
# --- Configuration ---
# 🛑 CRITICAL: Update this path to your model location 🛑
MODEL_PATH = r'C:\Users\Lenovo\OneDrive - aus.edu\FALL 25\SENIOR 2\iades\best.pt' 
DEVICE = 'cpu' # Use 'cpu' as specified in your script. Change to 'cuda' for GPU.
CONFIDENCE_THRESHOLD = 0.5 # Same as 'conf=0.5' in your prediction script
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

def run_live_detection():
    camera = None
    try:
        # Load the YOLO Model
        print(f"Loading model from: {MODEL_PATH} on device: {DEVICE}")
        model = YOLO(MODEL_PATH)
        
        # Initialize Camera
        if PICAMERA2_AVAILABLE:
            camera = Picamera2()
            config = camera.create_video_configuration(main={"size": (FRAME_WIDTH, FRAME_HEIGHT)})
            camera.configure(config)
            camera.start()
            print("Camera: Using Picamera2.")
        else:
            # Fallback for standard webcam (0 is usually the default camera)
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            if not camera.isOpened():
                 raise Exception("Could not open standard OpenCV camera (cv2.VideoCapture(0)).")
            print("Camera: Using cv2.VideoCapture(0).")

    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    # --- Main Detection Loop ---
    print("\nStarting live detection stream. Press 'q' to quit...")
    while True:
        try:
            # 1. Capture Frame
            if PICAMERA2_AVAILABLE:
                frame = camera.capture_array()
            else:
                ret, frame = camera.read()
                if not ret:
                    print("Error reading frame or end of stream.")
                    break
            
            # 2. Run Inference
            # The 'stream=True' and 'verbose=False' ensure efficient, quiet, real-time processing
            results = model.predict(
                source=frame,
                conf=CONFIDENCE_THRESHOLD,
                device=DEVICE,
                stream=True, 
                verbose=False
            )
            
            # 3. Process and Display the first result (most common case for a single frame)
            for result in results:
                # result.plot() handles drawing the bounding boxes and labels
                annotated_frame = result.plot() 
                
                # Display the frame
                cv2.imshow("YOLO Live Detection Stream", annotated_frame)
            
            # Check for 'q' key press (1ms delay)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        except Exception as e:
            # Catch errors that occur during the live loop (e.g., disconnection)
            print(f"\nAn error occurred in the detection loop: {e}")
            break

    # --- 4. Cleanup ---
    if camera:
        if PICAMERA2_AVAILABLE:
            camera.stop()
        else:
            camera.release()
    cv2.destroyAllWindows()
    print("Stream closed.")

if __name__ == "__main__":
    run_live_detection()