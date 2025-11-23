import serial
import time

serial_port = "/dev/ttyAMA0"
baud_rate = 9600

def parse_gga(fields):
    if len(fields) < 15:
        return None

    return {
        "fix_quality": fields[6],
        "satellites": int(fields[7]) if fields[7].isdigit() else 0,
        "hdop": fields[8],
        "altitude": fields[9]
    }

def parse_rmc(fields):
    if len(fields) < 12:
        return None

    return {
        "status": fields[2],
        "lat": f"{fields[3]} {fields[4]}",
        "lon": f"{fields[5]} {fields[6]}",
        "speed_knots": fields[7],
        "date": fields[9]
    }

def read_gps():
    try:
        ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=1)
        print(f"Connected to GPS on {serial_port}.")
        print("Reading data...\n")

        last_gga = None
        last_rmc = None
        no_sat_counter = 0
        no_data_counter = 0

        while True:
            line_bytes = ser.readline()

            # If no bytes came from GPS
            if not line_bytes:
                no_data_counter += 1
                if no_data_counter >= 5:
                    print("❌ No data received bro.")
                    no_data_counter = 0
                continue
            else:
                no_data_counter = 0  # Reset counter when data arrives

            # Decode line
            line = line_bytes.decode("utf-8", errors="ignore").strip()
            print(line)

            # Parse
            if line.startswith("$GPGGA"):
                last_gga = parse_gga(line.split(","))

            elif line.startswith("$GPRMC"):
                last_rmc = parse_rmc(line.split(","))

            # Display status
            if last_gga:
                sats = last_gga["satellites"]
                fix = last_gga["fix_quality"]

                print("\n------ GPS STATUS ------")
                print(f"Satellites tracked: {sats}")
                print(f"Fix quality: {fix} (0=No fix, 1=GPS, 2=DGPS)")

                if fix == "0":
                    print("⚠️ GPS has NO FIX.")
                else:
                    print("✅ GPS FIX ACQUIRED.")

                # Antenna check (inferred)
                if sats == 0:
                    no_sat_counter += 1
                else:
                    no_sat_counter = 0

                if no_sat_counter > 5:
                    print("🚨 ANTENNA WARNING: No satellites detected.")
                    print("Possible causes:")
                    print(" - No antenna connected")
                    print(" - Wrong antenna frequency")
                    print(" - Indoor / blocked sky")
                else:
                    print("Antenna status: OK (signal detected)")

                if last_rmc:
                    print(f"RMC Status: {last_rmc['status']} (A=Valid, V=Invalid)")
                    print(f"Latitude: {last_rmc['lat']}")
                    print(f"Longitude: {last_rmc['lon']}")
                    print(f"Speed (knots): {last_rmc['speed_knots']}")
                    print(f"Date: {last_rmc['date']}")

                print("------------------------\n")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nStopping.")
    except serial.SerialException as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    read_gps()
