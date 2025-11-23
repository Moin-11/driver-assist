from picamera2 import Picamera2
import time

picam2 = Picamera2()

picam2.start()          # <-- start camera without preview
time.sleep(2)

picam2.capture_file("test_image.jpg")
print("Captured!")
