import serial
import pynmea2
import time
import requests

# --- Constants ---
# Speed conversion factors
KNOTS_TO_KPH = 1.852
KNOTS_TO_MPS = 0.514444

# Server configuration for event emission
SERVER_URL = "http://localhost:8000/emit"
EMIT_EVENTS = True  # Set to False to disable event emission
EMIT_INTERVAL = 2.0  # Emit speed updates every 2 seconds


def emit_event(event_data):
    """
    Send event to the SSE server.
    Fails silently if server is unavailable to not crash the GPS module.
    """
    if not EMIT_EVENTS:
        return

    try:
        requests.post(SERVER_URL, json=event_data, timeout=0.1)
    except Exception:
        # Silently fail if server is not running
        pass

def get_gps_speed():
    """
    Connects to the GPS module, parses $GPRMC sentences,
    and prints the speed.
    """
    # The serial port is /dev/ttyAMA0 on the Raspberry Pi
    serial_port = "/dev/ttyAMA0"
    baud_rate = 9600

    try:
        # Open the serial port
        ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=1)
        print(f"Connected to GPS on {serial_port} at {baud_rate} baud.")
        print("Waiting for satellite fix to get speed...")
        print("Press Ctrl+C to stop.")

        last_emit_time = 0  # Track last event emission time

        while True:
            try:
                # Read a line of data from the serial port
                line = ser.readline().decode('utf-8')

                # We are only interested in the $GPRMC sentence,
                # which contains "Recommended Minimum" data including speed.
                if line.startswith('$GPRMC'):
                    # Parse the NMEA sentence
                    msg = pynmea2.parse(line)

                    # Check if the GPS has a valid fix (Status 'A')
                    if msg.status == 'A':
                        # msg.spd_over_grnd gives speed in knots
                        speed_knots = msg.spd_over_grnd

                        # Convert to other units
                        speed_kph = speed_knots * KNOTS_TO_KPH
                        speed_mps = speed_knots * KNOTS_TO_MPS
                        speed_mph = speed_kph * 0.621371  # Convert kph to mph

                        # Print the formatted speed
                        # \r prints on the same line (carriage return)
                        print(f"Speed: {speed_kph:.2f} km/h | {speed_knots:.2f} knots | {speed_mps:.2f} m/s   ", end="\r")

                        # Emit speed update event every EMIT_INTERVAL seconds
                        current_time = time.time()
                        if current_time - last_emit_time >= EMIT_INTERVAL:
                            event_data = {
                                'module': 'Speed Monitoring',
                                'type': 'speed_update',
                                'speed_kph': round(speed_kph, 1),
                                'speed_mph': round(speed_mph, 1),
                                'speed_mps': round(speed_mps, 1),
                                'gps_fix': True,
                                'severity': 'low',
                                'message': f'Current speed: {speed_mph:.0f} mph ({speed_kph:.0f} km/h)'
                            }
                            emit_event(event_data)
                            last_emit_time = current_time

                    else:
                        # No valid fix
                        print("Status: VOID. No satellite fix. Speed is 0.", end="\r")

                        # Emit GPS status update occasionally
                        current_time = time.time()
                        if current_time - last_emit_time >= EMIT_INTERVAL * 2:  # Less frequently for no-fix status
                            event_data = {
                                'module': 'Speed Monitoring',
                                'type': 'gps_status',
                                'gps_fix': False,
                                'severity': 'low',
                                'message': 'No GPS fix - waiting for satellites'
                            }
                            emit_event(event_data)
                            last_emit_time = current_time

            except pynmea2.ParseError:
                # print("ParseError: Could not parse sentence.")
                continue # Skip to the next line
            except UnicodeDecodeError:
                # print("UnicodeDecodeError: Garbled data.")
                continue # Skip to the next line
            except KeyboardInterrupt:
                print("\nStopping script.")
                break

    except serial.SerialException as e:
        print(f"Error: Could not open serial port {serial_port}.")
        print("Did you run 'sudo raspi-config' and disable the serial console?")
        print("Did you add your user to the 'dialout' group?")
        print(f"Details: {e}")
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    get_gps_speed()