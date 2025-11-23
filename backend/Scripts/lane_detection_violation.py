#!/usr/bin/env python3
"""
lane_detection_pi_violation.py
Real-time lane detection with unsignaled deviation (lane drift) violations.
Raspberry Pi 5 + AI Hat + Pi Camera (headless). CSV logging.

Author: Faris AlSafi & Team
"""

# Import-safety: Optional Pi-specific modules
try:
    from picamera2 import Picamera2  # type: ignore
    PICAMERA2_AVAILABLE = True
except Exception:
    PICAMERA2_AVAILABLE = False

import cv2
import numpy as np
import csv
import datetime
import time
import os
import argparse
import requests

# -------- GPIO (optional) --------
GPIO_AVAILABLE = False
BLINKER_LEFT_PIN = 17   # BCM pins; adjust to your wiring
BLINKER_RIGHT_PIN = 27
BUZZER_PIN = 22         # optional buzzer output
try:
    import RPi.GPIO as GPIO  # type: ignore
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BLINKER_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BLINKER_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # Optional buzzer:
    # GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO_AVAILABLE = True
except Exception:
    GPIO_AVAILABLE = False
    print("GPIO not available. Blinkers assumed OFF; buzzer disabled.")


def blinker_left_on():
    return GPIO.input(BLINKER_LEFT_PIN) == GPIO.HIGH if GPIO_AVAILABLE else False


def blinker_right_on():
    return GPIO.input(BLINKER_RIGHT_PIN) == GPIO.HIGH if GPIO_AVAILABLE else False


def buzz(ms=120):
    # if GPIO_AVAILABLE:
    #     GPIO.output(BUZZER_PIN, GPIO.HIGH)
    #     time.sleep(ms/1000.0)
    #     GPIO.output(BUZZER_PIN, GPIO.LOW)
    pass


# -------------------- CONFIG --------------------
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
ROI_HEIGHT_RATIO = 0.45
CANNY_THRESHOLDS = (50, 150)
MIN_LINE_LENGTH = 50
MAX_LINE_GAP = 150
CENTER_TOLERANCE = 40          # px for "centered"
DRIFT_MARGIN = 20              # extra px beyond tolerance to confirm drift
PERSIST_FRAMES = 6             # frames deviation must persist to count as event
VIOLATION_COOLDOWN_S = 3.0     # minimum time between violation flags
CSV_LOG_FILE = "lane_log.csv"

# Smoothing
EMA_ALPHA = 0.25               # 0..1; higher = more responsive, lower = smoother

# Server configuration for event emission
SERVER_URL = "http://localhost:8000/emit"
EMIT_EVENTS = True  # Set to False to disable event emission


# -------------------- LANE DETECTION --------------------
def region_of_interest(img):
    height = img.shape[0]
    polygons = np.array([[
        (0, height),
        (FRAME_WIDTH, height),
        (FRAME_WIDTH, int(height * ROI_HEIGHT_RATIO)),
        (0, int(height * ROI_HEIGHT_RATIO))
    ]])
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, polygons, 255)
    return cv2.bitwise_and(img, mask)


def detect_lanes(frame_rgb):
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, CANNY_THRESHOLDS[0], CANNY_THRESHOLDS[1])
    cropped = region_of_interest(edges)

    lines = cv2.HoughLinesP(
        cropped, 1, np.pi / 180, 50,
        minLineLength=MIN_LINE_LENGTH, maxLineGap=MAX_LINE_GAP
    )

    if lines is None:
        return None, 0, "no_lanes_detected"

    left_lines, right_lines = [], []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1 + 1e-6)
        if abs(slope) < 0.5:
            continue
        if slope < 0:
            left_lines.append(line[0])
        else:
            right_lines.append(line[0])

    if len(left_lines) == 0 or len(right_lines) == 0:
        return None, 0, "lane_boundary_missing"

    left_avg = np.mean(left_lines, axis=0).astype(int)
    right_avg = np.mean(right_lines, axis=0).astype(int)

    left_x2 = left_avg[2]
    right_x2 = right_avg[2]
    lane_center = (left_x2 + right_x2) // 2
    frame_center = FRAME_WIDTH // 2
    deviation = lane_center - frame_center

    if abs(deviation) <= CENTER_TOLERANCE:
        lane_state = "centered"
    elif deviation > 0:
        lane_state = "right_drift"
    else:
        lane_state = "left_drift"

    return lines, deviation, lane_state


# -------------------- STATE FOR VIOLATIONS --------------------
ema_dev = 0.0
left_persist = 0
right_persist = 0
last_violation_ts = 0.0


def update_ema(current, previous, alpha):
    return alpha * current + (1.0 - alpha) * previous


def emit_event(event_data):
    """
    Send event to the SSE server.
    Fails silently if server is unavailable to not crash the detection module.
    """
    if not EMIT_EVENTS:
        return

    try:
        requests.post(SERVER_URL, json=event_data, timeout=0.1)
    except Exception:
        # Silently fail if server is not running
        pass


def check_violation(ema_deviation, bl_left, bl_right, now):
    global left_persist, right_persist, last_violation_ts
    violation = ""

    # Determine drift beyond tolerance + margin
    if ema_deviation < -(CENTER_TOLERANCE + DRIFT_MARGIN):
        left_persist += 1
        right_persist = 0
        if left_persist >= PERSIST_FRAMES:
            if not bl_left and (now - last_violation_ts) > VIOLATION_COOLDOWN_S:
                violation = "unsignaled_left_deviation"
                left_persist = 0
                last_violation_ts = now
    elif ema_deviation > (CENTER_TOLERANCE + DRIFT_MARGIN):
        right_persist += 1
        left_persist = 0
        if right_persist >= PERSIST_FRAMES:
            if not bl_right and (now - last_violation_ts) > VIOLATION_COOLDOWN_S:
                violation = "unsignaled_right_deviation"
                right_persist = 0
                last_violation_ts = now
    else:
        # Back near center; decay counters
        left_persist = max(0, left_persist - 1)
        right_persist = max(0, right_persist - 1)

    return violation


# -------------------- SYNTHETIC SELF-TEST --------------------
def make_synthetic_frame(drift_px=0):
    """Create a simple synthetic road image with two lane lines.
    drift_px shifts the lane center to simulate deviation.
    Returns an RGB frame.
    """
    img = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    center_x = FRAME_WIDTH // 2 + int(drift_px)
    lane_half = 120
    thickness = 6
    color = (255, 255, 255)

    # Draw two slanted lane lines
    # Left line
    cv2.line(img, (center_x - lane_half, FRAME_HEIGHT),
             (center_x - lane_half - 60, int(FRAME_HEIGHT * ROI_HEIGHT_RATIO)), color, thickness)
    # Right line
    cv2.line(img, (center_x + lane_half, FRAME_HEIGHT),
             (center_x + lane_half + 60, int(FRAME_HEIGHT * ROI_HEIGHT_RATIO)), color, thickness)

    # Already RGB
    return img


def run_synthetic_test(num_cases=3):
    print("Running synthetic self-test...")
    tests = [0, -70, 70][:max(1, num_cases)]
    for drift in tests:
        frame = make_synthetic_frame(drift)
        _, dev, state = detect_lanes(frame)
        print(f"drift={drift:+4d}px -> deviation={dev:+4d}px state={state}")
    print("Synthetic test complete.")


# -------------------- MAIN LOOP --------------------
def main():
    parser = argparse.ArgumentParser(description="Lane detection with unsignaled deviation logging (headless)")
    parser.add_argument("--csv", default=CSV_LOG_FILE, help="Path to CSV log file")
    parser.add_argument("--force-opencv", action="store_true", help="Force OpenCV camera backend instead of Picamera2")
    parser.add_argument("--device-id", type=int, default=0, help="OpenCV camera device id")
    parser.add_argument("--sleep", type=float, default=0.1, help="Sleep between frames (s)")
    parser.add_argument("--synthetic-test", type=int, default=0, help="Run N synthetic tests then exit")
    args = parser.parse_args()

    if args.synthetic_test > 0:
        run_synthetic_test(args.synthetic_test)
        return

    # CSV init
    csv_path = args.csv
    fresh_file = not os.path.exists(csv_path)
    with open(csv_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        if fresh_file:
            writer.writerow([
                "Timestamp",
                "LaneState",
                "Deviation(px)",
                "EMA_Deviation(px)",
                "BlinkerLeft",
                "BlinkerRight",
                "Violation"
            ])

    print("🟢 Lane detection with unsignaled deviation started... Ctrl+C to stop.\n")

    cap = None
    picam2 = None
    using_picam2 = PICAMERA2_AVAILABLE and not args.force_opencv

    try:
        if using_picam2:
            picam2 = Picamera2()
            picam2.preview_configuration.main.size = (FRAME_WIDTH, FRAME_HEIGHT)
            picam2.preview_configuration.main.format = "RGB888"
            picam2.configure("preview")
            picam2.start()
        else:
            cap = cv2.VideoCapture(args.device_id)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        global ema_dev
        ema_dev = 0.0

        while True:
            if using_picam2:
                frame_rgb = picam2.capture_array()  # RGB
            else:
                ret, frame_bgr = cap.read()
                if not ret:
                    continue
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

            _, deviation, lane_state = detect_lanes(frame_rgb)

            # Smooth deviation for stability
            ema_dev = update_ema(deviation, ema_dev, EMA_ALPHA)

            # Read blinkers
            bl_left = blinker_left_on()
            bl_right = blinker_right_on()

            now = time.time()
            violation = check_violation(ema_dev, bl_left, bl_right, now)
            if violation:
                print(f"⚠️  {violation.replace('_',' ').title()} | EMA deviation: {ema_dev:.1f}px")
                buzz(120)

                # Emit event to server
                direction = 'left' if 'left' in violation else 'right'
                from_lane = 'Center'
                to_lane = 'Left' if direction == 'left' else 'Right'

                # Calculate safety score (0-100, lower is worse)
                safety_score = max(0, 100 - int(abs(ema_dev)))

                event_data = {
                    'module': 'Lane Change Detection',
                    'eventType': f'{from_lane} to {to_lane}',
                    'fromLane': from_lane,
                    'toLane': to_lane,
                    'direction': direction,
                    'deviation_px': round(ema_dev, 1),
                    'signalUsed': False,
                    'safetyScore': safety_score,
                    'severity': 'high',
                    'message': f'⚠️ Lane change WITHOUT signal! Moved from {from_lane} to {to_lane} lane. Use turn signals!'
                }
                emit_event(event_data)

            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] State: {lane_state:18s} dev: {deviation:6.1f}px ema: {ema_dev:6.1f}px "
                  f"BL:{int(bl_left)} BR:{int(bl_right)} {'| ' + violation if violation else ''}")

            with open(csv_path, mode="a", newline="") as file:
                csv.writer(file).writerow([
                    ts, lane_state, round(deviation, 2), round(ema_dev, 2),
                    int(bl_left), int(bl_right), violation
                ])

            time.sleep(args.sleep)  # adjust to your target FPS

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        try:
            if using_picam2 and picam2 is not None:
                picam2.stop()
        except Exception:
            pass
        try:
            if cap is not None:
                cap.release()
        except Exception:
            pass
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except Exception:
                pass
        print(f"✅ Log saved to {csv_path}")


if __name__ == "__main__":
    main()


