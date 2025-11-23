from picamera2 import Picamera2
import cv2
import numpy as np
import time
from collections import deque

# Store history of lanes for smoothing
left_history = deque(maxlen=10)
right_history = deque(maxlen=10)

def average_lane(lines):
    if len(lines) == 0:
        return None
    x1 = int(np.mean([l[0] for l in lines]))
    y1 = int(np.mean([l[1] for l in lines]))
    x2 = int(np.mean([l[2] for l in lines]))
    y2 = int(np.mean([l[3] for l in lines]))
    return (x1, y1, x2, y2)

picam2 = Picamera2()
config = picam2.create_video_configuration({"size": (1280, 720)})
picam2.configure(config)
picam2.start()

time.sleep(1)

while True:
    frame = picam2.capture_array()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    height, width = edges.shape
    mask = np.zeros_like(edges)

    polygon = np.array([[
        (0, height),
        (width, height),
        (int(width * 0.5), int(height * 0.55))
    ]], dtype=np.int32)

    cv2.fillPoly(mask, polygon, 255)
    roi = cv2.bitwise_and(edges, mask)

    # Hough transform:
    lines = cv2.HoughLinesP(
        roi,
        rho=1,
        theta=np.pi/180,
        threshold=50,
        minLineLength=80,
        maxLineGap=150
    )

    left_lines = []
    right_lines = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1 + 1e-6)

            # Only accept strong lane-like slopes
            if slope < -0.4:
                left_lines.append((x1, y1, x2, y2))
            elif slope > 0.4:
                right_lines.append((x1, y1, x2, y2))

    # Smooth lanes using history
    if left_lines:
        left_history.append(average_lane(left_lines))
    if right_lines:
        right_history.append(average_lane(right_lines))

    left_lane = average_lane(left_history)
    right_lane = average_lane(right_history)

    # Draw stabilized lanes
    if left_lane:
        cv2.line(frame, (left_lane[0], left_lane[1]), (left_lane[2], left_lane[3]), (0,255,0), 5)

    if right_lane:
        cv2.line(frame, (right_lane[0], right_lane[1]), (right_lane[2], right_lane[3]), (0,255,0), 5)

    cv2.imshow("Stabilized Lane Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
