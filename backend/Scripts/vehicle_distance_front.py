#!/usr/bin/env python3
"""
Front Vehicle Distance Estimation using YOLO and Perspective Geometry

This script captures frames from a Raspberry Pi Camera (or any OpenCV camera),
detects vehicles using Ultralytics YOLO, and estimates distance to vehicles in
front using a simple pinhole camera model. It highlights the closest vehicle
in the central ROI and prints a rough distance estimate.

Based on concepts from: https://github.com/kemalkilicaslan/Vehicle-Distance-Measurement-System
"""

import time
from pathlib import Path
from typing import Tuple, Dict, List

import numpy as np
import cv2
from ultralytics import YOLO
try:
    import openvino as ov  # optional; improves CPU perf if installed
except Exception:
    ov = None
try:
    import hailo  # placeholder for Hailo SDK presence check
except Exception:
    hailo = None


# ========= Configuration =========
# Camera index or pipeline; for Pi Camera via libcamera, you may need a different pipeline
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
DISPLAY = True

# YOLO model (downloads on first use)
YOLO_MODEL = 'yolov8n.pt'  # lightweight; change to yolov8s.pt for better accuracy
VEHICLE_CLASS_IDS = {2, 3, 5, 7}  # COCO: car=2, motorcycle=3, bus=5, truck=7
DETECTION_CONFIDENCE = 0.35

# Simple central ROI polygon (fractional coordinates of frame)
ROI_FRAC = np.array([[0.35, 0.55], [0.65, 0.55], [0.85, 1.0], [0.15, 1.0]], dtype=np.float32)

# Distance estimation parameters
FOCAL_LENGTH_PX = 900.0   # pixels; requires calibration for your camera
REF_HEIGHTS_M = {         # nominal real heights per class (rough values)
    2: 1.55,  # car roofline
    3: 1.20,  # motorcycle rider height
    5: 3.00,  # bus
    7: 2.50,  # truck
}
PERSPECTIVE_ALPHA = 0.0005  # small correction for off-center targets


def make_roi_polygon(w: int, h: int) -> np.ndarray:
    pts = (ROI_FRAC * np.array([w, h], dtype=np.float32)).astype(np.int32)
    return pts.reshape((-1, 1, 2))


def in_roi(bbox: Tuple[int, int, int, int], roi_mask: np.ndarray) -> bool:
    x1, y1, x2, y2 = bbox
    cx, cy = (x1 + x2) // 2, y2
    return roi_mask[cy, cx] > 0


def estimate_distance_m(bbox: Tuple[int, int, int, int], cls_id: int, frame_center: Tuple[int, int]) -> float:
    x1, y1, x2, y2 = bbox
    h_img = max(1, y2 - y1)
    h_real = REF_HEIGHTS_M.get(cls_id, 1.55)
    # pinhole: d ≈ f * h_real / h_img
    d = (FOCAL_LENGTH_PX * h_real) / float(h_img)
    # perspective correction for off-axis
    cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    dx = (cx - frame_center[0])
    d *= (1.0 + PERSPECTIVE_ALPHA * abs(dx))
    return float(max(0.1, d))


def draw_annotations(frame: np.ndarray, closest: Dict, roi_poly: np.ndarray) -> None:
    overlay = frame.copy()
    cv2.fillPoly(overlay, [roi_poly], (0, 255, 0))
    frame[:] = cv2.addWeighted(overlay, 0.12, frame, 0.88, 0)
    if not closest:
        return
    x1, y1, x2, y2 = closest['bbox']
    dist_m = closest['distance_m']
    color = (0, 0, 255) if dist_m < 10 else (0, 200, 0)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    label = f"{closest['name']} ~ {dist_m:.1f} m"
    cv2.putText(frame, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)


def run():
    import argparse
    parser = argparse.ArgumentParser(description='Front vehicle distance (YOLO)')
    parser.add_argument('--backend', choices=['ultralytics', 'openvino', 'hailo'], default='ultralytics',
                        help='Inference backend')
    parser.add_argument('--model', default=YOLO_MODEL, help='YOLO model or exported model path')
    parser.add_argument('--camera', type=int, default=CAMERA_INDEX, help='OpenCV camera index')
    parser.add_argument('--width', type=int, default=FRAME_WIDTH)
    parser.add_argument('--height', type=int, default=FRAME_HEIGHT)
    parser.add_argument('--display', action='store_true', default=DISPLAY)
    parser.add_argument('--hef', default='', help='Hailo HEF path (if using hailo backend)')
    args = parser.parse_args()

    backend = args.backend
    model_path = args.model
    use_display = args.display

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    if not cap.isOpened():
        print("Failed to open camera")
        return

    # Build ROI for the requested frame size
    roi_poly = make_roi_polygon(args.width, args.height)
    roi_mask = np.zeros((args.height, args.width), dtype=np.uint8)
    cv2.fillPoly(roi_mask, [roi_poly], 255)
    cx = args.width // 2
    cy = args.height // 2

    # Select backend
    ov_model = None
    if backend == 'openvino':
        try:
            # Export once if plain .pt provided
            if model_path.endswith('.pt'):
                base = Path(model_path).stem
                out_dir = Path('models')
                out_dir.mkdir(exist_ok=True)
                exported = out_dir / f'{base}_openvino_model'
                if not (exported.with_suffix('.xml')).exists():
                    YOLO(model_path).export(format='openvino', dynamic=False, half=True, imgsz=(args.height, args.width), opset=13, optimize=True)
                model_path = str(exported)
            ov_model = YOLO(model_path)
        except Exception as e:
            print(f"OpenVINO backend unavailable, falling back to Ultralytics CPU: {e}")
            backend = 'ultralytics'

    if backend == 'hailo':
        if hailo is None or not args.hef:
            print("Hailo SDK/HEF not found. Falling back to Ultralytics CPU. Provide --hef and install Hailo SDK.")
            backend = 'ultralytics'

    if backend == 'ultralytics':
        model = YOLO(model_path)
    elif backend == 'openvino':
        model = ov_model
    else:
        model = YOLO(model_path)  # safety fallback

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.02)
                continue

            results = model.predict(source=frame, conf=DETECTION_CONFIDENCE, verbose=False)[0]
            boxes = results.boxes

            candidates: List[Dict] = []
            if boxes is not None and len(boxes) > 0:
                for b in boxes:
                    cls_id = int(b.cls)
                    if cls_id not in VEHICLE_CLASS_IDS:
                        continue
                    x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                    if x1 < 0 or y1 < 0 or x2 >= FRAME_WIDTH or y2 >= FRAME_HEIGHT:
                        x1 = max(0, x1); y1 = max(0, y1)
                        x2 = min(FRAME_WIDTH - 1, x2); y2 = min(FRAME_HEIGHT - 1, y2)
                    if x2 <= x1 or y2 <= y1:
                        continue
                    if not in_roi((x1, y1, x2, y2), roi_mask):
                        continue
                    dist_m = estimate_distance_m((x1, y1, x2, y2), cls_id, (cx, cy))
                    name = results.names.get(cls_id, f"cls{cls_id}")
                    candidates.append({'bbox': (x1, y1, x2, y2), 'distance_m': dist_m, 'name': name})

            closest = min(candidates, key=lambda d: d['distance_m']) if candidates else {}
            draw_annotations(frame, closest, roi_poly)

            if closest:
                print(f"Closest front vehicle: {closest['name']} ~ {closest['distance_m']:.1f} m")

            if use_display:
                cv2.imshow('Front Distance', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        cap.release()
        if use_display:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    run()


