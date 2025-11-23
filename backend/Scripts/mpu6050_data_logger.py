#!/usr/bin/env python3
"""
MPU6050 Data Logger for Driver Behavior Analysis

This script provides comprehensive data logging capabilities for MPU6050 IMU sensors
connected to a Raspberry Pi. It continuously captures accelerometer and gyroscope
data with precise timestamps and saves it to CSV files for offline analysis.

Key Features:
- Continuous sensor data collection via I2C communication
- High-precision timestamping for temporal analysis
- Configurable sampling rates and output directories
- Graceful shutdown handling with signal management
- CSV output format compatible with analysis tools
- Real-time data validation and error handling

Hardware Requirements:
- Raspberry Pi with I2C enabled
- MPU6050 IMU sensor connected via I2C (SDA/SCL pins)
- Proper power supply (3.3V for MPU6050)

Usage Examples:
    # Basic logging with default settings
    python mpu6050_data_logger.py
    
    # Custom sampling rate and output directory
    python mpu6050_data_logger.py --sample-rate 100 --output-dir /path/to/logs
    
    # Specific I2C bus and address
    python mpu6050_data_logger.py --bus 1 --address 0x68

Author: Driver Behavior Analysis System
Version: 1.0
"""

# Standard library imports
import time          # For timing control and sleep operations
import csv          # For CSV file writing and data formatting
import datetime     # For timestamp generation and date handling
import signal       # For graceful shutdown signal handling
import sys          # For system-specific parameters and functions
from pathlib import Path  # For cross-platform path handling
import argparse     # For command-line argument parsing
import json        # For configuration file handling

# Third-party library imports with error handling
try:
    import smbus           # For I2C communication with MPU6050 sensor
    import numpy as np     # For numerical computations and data processing
except ImportError as e:
    print("Required libraries not found. Please install:")
    print("pip install smbus numpy")
    print(f"Missing library: {e}")
    sys.exit(1)

class MPU6050:
    """
    MPU6050 IMU Sensor Interface for Data Logging
    
    This class provides a comprehensive interface to the MPU6050 6-axis IMU sensor
    specifically designed for data logging applications. It handles I2C communication,
    sensor initialization, data reading, and provides robust error handling for
    continuous data collection scenarios.
    
    Key Features:
    - High-precision sensor data collection
    - Automatic sensor initialization and configuration
    - Robust error handling for continuous operation
    - Optimized for data logging applications
    - Support for various sampling rates and configurations
    
    Hardware Connections:
    - VCC: 3.3V power supply
    - GND: Ground
    - SCL: I2C clock line (GPIO 3 on Raspberry Pi)
    - SDA: I2C data line (GPIO 2 on Raspberry Pi)
    - AD0: Ground (sets I2C address to 0x68)
    """
    
    # MPU6050 Registers
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F
    GYRO_XOUT_H = 0x43
    GYRO_YOUT_H = 0x45
    GYRO_ZOUT_H = 0x47
    
    def __init__(self, bus=1, address=0x68):
        """
        Initialize MPU6050 sensor.
        
        Args:
            bus (int): I2C bus number (usually 1 for Raspberry Pi)
            address (int): I2C address of MPU6050 (0x68 or 0x69)
        """
        self.bus = smbus.SMBus(bus)
        self.address = address
        self.initialized = False
        
    def initialize(self):
        """Initialize the MPU6050 sensor."""
        try:
            # Wake up the MPU6050
            self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)
            
            # Set sample rate to 1kHz
            self.bus.write_byte_data(self.address, self.SMPLRT_DIV, 7)
            
            # Configure accelerometer (±2g)
            self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0)
            
            # Configure gyroscope (±250°/s)
            self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0)
            
            # Configure DLPF (Digital Low Pass Filter)
            self.bus.write_byte_data(self.address, self.CONFIG, 6)
            
            self.initialized = True
            print("MPU6050 initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize MPU6050: {e}")
            self.initialized = False
    
    def read_word_2c(self, addr):
        """Read a 16-bit signed value from the MPU6050."""
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr + 1)
        val = (high << 8) + low
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val
    
    def get_accel_data(self):
        """Get accelerometer data in g units."""
        if not self.initialized:
            return None
            
        accel_x = self.read_word_2c(self.ACCEL_XOUT_H) / 16384.0
        accel_y = self.read_word_2c(self.ACCEL_YOUT_H) / 16384.0
        accel_z = self.read_word_2c(self.ACCEL_ZOUT_H) / 16384.0
        
        return accel_x, accel_y, accel_z
    
    def get_gyro_data(self):
        """Get gyroscope data in degrees per second."""
        if not self.initialized:
            return None
            
        gyro_x = self.read_word_2c(self.GYRO_XOUT_H) / 131.0
        gyro_y = self.read_word_2c(self.GYRO_YOUT_H) / 131.0
        gyro_z = self.read_word_2c(self.GYRO_ZOUT_H) / 131.0
        
        return gyro_x, gyro_y, gyro_z
    
    def get_all_data(self):
        """Get both accelerometer and gyroscope data."""
        accel = self.get_accel_data()
        gyro = self.get_gyro_data()
        
        if accel is None or gyro is None:
            return None
            
        return {
            'accel_x': accel[0],
            'accel_y': accel[1], 
            'accel_z': accel[2],
            'gyro_x': gyro[0],
            'gyro_y': gyro[1],
            'gyro_z': gyro[2]
        }

class DataLogger:
    """
    Data logger for MPU6050 sensor data.
    """
    
    def __init__(self, output_dir="logs", sample_rate=50):
        """
        Initialize data logger.
        
        Args:
            output_dir (str): Directory to save log files
            sample_rate (int): Sampling rate in Hz
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.sample_rate = sample_rate
        self.sample_interval = 1.0 / sample_rate
        self.running = False
        self.csv_file = None
        self.csv_writer = None
        self.sample_count = 0
        
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = self.output_dir / f"mpu6050_data_{timestamp}.csv"
        
    def start_logging(self):
        """Start data logging to CSV file."""
        try:
            self.csv_file = open(self.filename, 'w', newline='')
            fieldnames = [
                'timestamp', 'sample_number', 
                'accel_x', 'accel_y', 'accel_z',
                'gyro_x', 'gyro_y', 'gyro_z',
                'accel_magnitude', 'gyro_magnitude'
            ]
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            self.csv_writer.writeheader()
            self.running = True
            print(f"Started logging to {self.filename}")
            print("Press Ctrl+C to stop logging")
            
        except Exception as e:
            print(f"Failed to start logging: {e}")
            self.running = False
    
    def log_data(self, sensor_data):
        """
        Log sensor data to CSV.
        
        Args:
            sensor_data (dict): Sensor data from MPU6050
        """
        if not self.running or self.csv_writer is None:
            return
            
        try:
            timestamp = datetime.datetime.now().isoformat()
            self.sample_count += 1
            
            # Calculate magnitudes
            accel_magnitude = np.sqrt(
                sensor_data['accel_x']**2 + 
                sensor_data['accel_y']**2 + 
                sensor_data['accel_z']**2
            )
            gyro_magnitude = np.sqrt(
                sensor_data['gyro_x']**2 + 
                sensor_data['gyro_y']**2 + 
                sensor_data['gyro_z']**2
            )
            
            # Write data to CSV
            row = {
                'timestamp': timestamp,
                'sample_number': self.sample_count,
                'accel_x': sensor_data['accel_x'],
                'accel_y': sensor_data['accel_y'],
                'accel_z': sensor_data['accel_z'],
                'gyro_x': sensor_data['gyro_x'],
                'gyro_y': sensor_data['gyro_y'],
                'gyro_z': sensor_data['gyro_z'],
                'accel_magnitude': accel_magnitude,
                'gyro_magnitude': gyro_magnitude
            }
            
            self.csv_writer.writerow(row)
            self.csv_file.flush()  # Ensure data is written immediately
            
        except Exception as e:
            print(f"Error logging data: {e}")
    
    def stop_logging(self):
        """Stop data logging and close file."""
        self.running = False
        if self.csv_file:
            self.csv_file.close()
            print(f"Stopped logging. Total samples: {self.sample_count}")
            print(f"Data saved to: {self.filename}")

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to gracefully stop logging."""
    print("\nStopping data logger...")
    global logger, mpu
    if logger:
        logger.stop_logging()
    sys.exit(0)

def main():
    """Main function to run the data logger."""
    parser = argparse.ArgumentParser(description='MPU6050 Data Logger')
    parser.add_argument('--output-dir', default='logs', 
                       help='Output directory for log files (default: logs)')
    parser.add_argument('--sample-rate', type=int, default=50,
                       help='Sampling rate in Hz (default: 50)')
    parser.add_argument('--bus', type=int, default=1,
                       help='I2C bus number (default: 1)')
    parser.add_argument('--address', default='0x68',
                       help='I2C address (default: 0x68)')
    
    args = parser.parse_args()
    
    # Convert address to integer
    address = int(args.address, 16)
    
    # Initialize MPU6050
    print("Initializing MPU6050...")
    mpu = MPU6050(bus=args.bus, address=address)
    mpu.initialize()
    
    if not mpu.initialized:
        print("Failed to initialize MPU6050. Exiting.")
        return
    
    # Initialize data logger
    logger = DataLogger(output_dir=args.output_dir, sample_rate=args.sample_rate)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start logging
    logger.start_logging()
    
    if not logger.running:
        print("Failed to start logging. Exiting.")
        return
    
    # Main logging loop
    try:
        while logger.running:
            start_time = time.time()
            
            # Read sensor data
            sensor_data = mpu.get_all_data()
            if sensor_data:
                logger.log_data(sensor_data)
                
                # Print status every 100 samples
                if logger.sample_count % 100 == 0:
                    print(f"Logged {logger.sample_count} samples...")
            
            # Maintain sample rate
            elapsed = time.time() - start_time
            sleep_time = max(0, logger.sample_interval - elapsed)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        pass
    finally:
        logger.stop_logging()

if __name__ == "__main__":
    main()

