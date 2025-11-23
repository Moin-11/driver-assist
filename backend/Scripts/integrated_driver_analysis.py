#!/usr/bin/env python3
"""
Integrated Driver Behavior Analysis System

This script combines MPU6050 data logging with real-time driver behavior analysis.
It logs all sensor data to CSV while providing real-time feedback on driving behavior.
"""

import time
import csv
import datetime
import signal
import sys
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
import argparse
from collections import deque
import json
import requests

try:
    import smbus
except ImportError:
    print("Required libraries not found. Please install:")
    print("pip install smbus")
    sys.exit(1)

from predict_driver_behavior import predict_from_raw_sensors

# Server configuration for event emission
SERVER_URL = "http://localhost:8000/emit"
EMIT_EVENTS = True  # Set to False to disable event emission

# Thresholds for brake event detection
HARD_BRAKE_THRESHOLD = 1.5  # g-force threshold for hard braking
MODERATE_BRAKE_THRESHOLD = 1.0  # g-force threshold for moderate braking

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


class IntegratedDriverAnalysis:
    """
    Integrated system for logging MPU6050 data and analyzing driver behavior.
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
    
    def __init__(self, output_dir="logs", sample_rate=50, window_size=50, 
                 model_path="models/driver_behavior_model.pkl", bus=1, address=0x68):
        """
        Initialize the integrated analysis system.
        
        Args:
            output_dir (str): Directory to save log files
            sample_rate (int): Sampling rate in Hz
            window_size (int): Size of sliding window for analysis
            model_path (str): Path to trained model
            bus (int): I2C bus number
            address (int): I2C address of MPU6050
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.sample_rate = sample_rate
        self.sample_interval = 1.0 / sample_rate
        self.window_size = window_size
        
        # MPU6050 setup
        self.bus = smbus.SMBus(bus)
        self.address = address
        self.initialized = False
        
        # Data logging
        self.csv_file = None
        self.csv_writer = None
        self.sample_count = 0
        self.running = False
        
        # Analysis buffers
        self.accel_buffer = deque(maxlen=window_size)
        self.gyro_buffer = deque(maxlen=window_size)
        self.timestamp_buffer = deque(maxlen=window_size)
        
        # Analysis results
        self.current_behavior = None
        self.behavior_history = []
        self.analysis_count = 0

        # Track last behavior to detect changes
        self.last_emitted_behavior = None
        self.last_brake_event_time = 0
        
        # Load model
        self.model_path = model_path
        self.load_model()
        
        # Behavior classification
        self.behavior_types = {
            1: "Normal Driving",
            2: "Moderate Driving", 
            3: "Aggressive Driving",
            4: "Dangerous Driving"
        }
        
        self.risk_levels = {
            1: "Low",
            2: "Low-Medium",
            3: "High",
            4: "Very High"
        }
        
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = self.output_dir / f"integrated_analysis_{timestamp}.csv"
        self.analysis_filename = self.output_dir / f"behavior_analysis_{timestamp}.json"
        
    def initialize_mpu6050(self):
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
    
    def get_sensor_data(self):
        """Get current sensor data from MPU6050."""
        if not self.initialized:
            return None
            
        # Get accelerometer data
        accel_x = self.read_word_2c(self.ACCEL_XOUT_H) / 16384.0
        accel_y = self.read_word_2c(self.ACCEL_YOUT_H) / 16384.0
        accel_z = self.read_word_2c(self.ACCEL_ZOUT_H) / 16384.0
        
        # Get gyroscope data
        gyro_x = self.read_word_2c(self.GYRO_XOUT_H) / 131.0
        gyro_y = self.read_word_2c(self.GYRO_YOUT_H) / 131.0
        gyro_z = self.read_word_2c(self.GYRO_ZOUT_H) / 131.0
        
        return {
            'accel_x': accel_x,
            'accel_y': accel_y,
            'accel_z': accel_z,
            'gyro_x': gyro_x,
            'gyro_y': gyro_y,
            'gyro_z': gyro_z
        }
    
    def load_model(self):
        """Load the trained model."""
        try:
            if Path(self.model_path).exists():
                self.model = joblib.load(self.model_path)
                print("Model loaded successfully")
            else:
                print(f"Model not found at {self.model_path}")
                print("Using basic prediction function")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Using basic prediction function")
    
    def start_logging(self):
        """Start data logging to CSV file."""
        try:
            self.csv_file = open(self.filename, 'w', newline='')
            fieldnames = [
                'timestamp', 'sample_number', 
                'accel_x', 'accel_y', 'accel_z',
                'gyro_x', 'gyro_y', 'gyro_z',
                'accel_magnitude', 'gyro_magnitude',
                'behavior_class', 'behavior_type', 'risk_level', 'confidence'
            ]
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            self.csv_writer.writeheader()
            self.running = True
            print(f"Started integrated logging to {self.filename}")
            print("Press Ctrl+C to stop")
            
        except Exception as e:
            print(f"Failed to start logging: {e}")
            self.running = False
    
    def analyze_behavior(self, sensor_data):
        """
        Analyze driver behavior using current sensor data.
        
        Args:
            sensor_data (dict): Current sensor readings
        """
        try:
            # Add to buffers
            accel_data = (sensor_data['accel_x'], sensor_data['accel_y'], sensor_data['accel_z'])
            gyro_data = (sensor_data['gyro_x'], sensor_data['gyro_y'], sensor_data['gyro_z'])
            
            self.accel_buffer.append(accel_data)
            self.gyro_buffer.append(gyro_data)
            self.timestamp_buffer.append(datetime.datetime.now().isoformat())
            
            # Analyze when buffer is full
            if len(self.accel_buffer) == self.window_size:
                # Make prediction
                result = predict_from_raw_sensors(
                    gyro_x=sensor_data['gyro_x'],
                    gyro_y=sensor_data['gyro_y'],
                    gyro_z=sensor_data['gyro_z'],
                    acc_x=sensor_data['accel_x'],
                    acc_y=sensor_data['accel_y'],
                    acc_z=sensor_data['accel_z']
                )
                
                # Store current behavior
                self.current_behavior = {
                    'class': result['predicted_class'],
                    'confidence': result['confidence'],
                    'behavior_type': self.behavior_types[result['predicted_class']],
                    'risk_level': self.risk_levels[result['predicted_class']],
                    'timestamp': self.timestamp_buffer[-1],
                    'accel_magnitude': np.linalg.norm(accel_data),
                    'gyro_magnitude': np.linalg.norm(gyro_data)
                }
                
                self.behavior_history.append(self.current_behavior.copy())
                self.analysis_count += 1

                # Emit events for significant behaviors or braking
                self.check_and_emit_events(sensor_data)

                # Keep only recent history
                if len(self.behavior_history) > 100:
                    self.behavior_history = self.behavior_history[-100:]
                    
        except Exception as e:
            print(f"Error in behavior analysis: {e}")

    def check_and_emit_events(self, sensor_data):
        """
        Check for significant events and emit to server.
        Emits brake events based on acceleration magnitude.
        """
        if not self.current_behavior:
            return

        accel_mag = self.current_behavior['accel_magnitude']
        behavior_class = self.current_behavior['class']
        current_time = time.time()

        # Estimate speed from behavior (rough estimation for prototype)
        # In production, integrate with GPS module
        estimated_speed_mph = 45  # Default estimate
        if behavior_class == 1:  # Normal
            estimated_speed_mph = 35
        elif behavior_class == 2:  # Moderate
            estimated_speed_mph = 50
        elif behavior_class == 3:  # Aggressive
            estimated_speed_mph = 60
        elif behavior_class == 4:  # Dangerous
            estimated_speed_mph = 70

        # Check for brake events based on acceleration magnitude
        # Cooldown: Don't emit events more frequently than every 2 seconds
        if current_time - self.last_brake_event_time > 2.0:
            brake_event = None

            if accel_mag > HARD_BRAKE_THRESHOLD:
                brake_event = {
                    'module': 'Brake Checking',
                    'eventType': 'hard',
                    'force': min(100, int(accel_mag * 50)),  # Convert to 0-100 scale
                    'speed': estimated_speed_mph,
                    'behavior_class': behavior_class,
                    'accel_magnitude': round(accel_mag, 2),
                    'severity': 'high',
                    'message': f'⚠️ HARD BRAKING DETECTED at {estimated_speed_mph} mph! Maintain safe following distance.'
                }
            elif accel_mag > MODERATE_BRAKE_THRESHOLD:
                brake_event = {
                    'module': 'Brake Checking',
                    'eventType': 'moderate',
                    'force': min(100, int(accel_mag * 50)),
                    'speed': estimated_speed_mph,
                    'behavior_class': behavior_class,
                    'accel_magnitude': round(accel_mag, 2),
                    'severity': 'moderate',
                    'message': f'⚡ Moderate braking at {estimated_speed_mph} mph. Monitor traffic ahead.'
                }

            if brake_event:
                emit_event(brake_event)
                self.last_brake_event_time = current_time

        # Emit behavior change events (only for Aggressive/Dangerous driving)
        if behavior_class >= 3 and self.last_emitted_behavior != behavior_class:
            behavior_event = {
                'module': 'Brake Checking',
                'eventType': 'behavior_change',
                'behavior_class': behavior_class,
                'behavior_type': self.current_behavior['behavior_type'],
                'risk_level': self.current_behavior['risk_level'],
                'confidence': round(self.current_behavior['confidence'], 2),
                'severity': 'high' if behavior_class == 4 else 'moderate',
                'message': f'⚠️ {self.current_behavior["behavior_type"]} detected! Risk Level: {self.current_behavior["risk_level"]}'
            }
            emit_event(behavior_event)
            self.last_emitted_behavior = behavior_class

    def log_data(self, sensor_data):
        """
        Log sensor data and analysis to CSV.
        
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
            
            # Get current behavior info
            behavior_class = self.current_behavior['class'] if self.current_behavior else 0
            behavior_type = self.current_behavior['behavior_type'] if self.current_behavior else "Unknown"
            risk_level = self.current_behavior['risk_level'] if self.current_behavior else "Unknown"
            confidence = self.current_behavior['confidence'] if self.current_behavior else 0.0
            
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
                'gyro_magnitude': gyro_magnitude,
                'behavior_class': behavior_class,
                'behavior_type': behavior_type,
                'risk_level': risk_level,
                'confidence': confidence
            }
            
            self.csv_writer.writerow(row)
            self.csv_file.flush()
            
        except Exception as e:
            print(f"Error logging data: {e}")
    
    def print_status(self):
        """Print current analysis status."""
        if self.current_behavior:
            print(f"\n{'='*60}")
            print(f"Integrated Driver Analysis - Sample {self.sample_count}")
            print(f"{'='*60}")
            print(f"Current Behavior: {self.current_behavior['behavior_type']}")
            print(f"Risk Level: {self.current_behavior['risk_level']}")
            print(f"Confidence: {self.current_behavior['confidence']:.3f}")
            print(f"Accel Magnitude: {self.current_behavior['accel_magnitude']:.3f} g")
            print(f"Gyro Magnitude: {self.current_behavior['gyro_magnitude']:.3f} °/s")
            print(f"Analyses Completed: {self.analysis_count}")
            
            # Print statistics every 20 analyses
            if self.analysis_count % 20 == 0 and self.analysis_count > 0:
                self.print_statistics()
    
    def print_statistics(self):
        """Print analysis statistics."""
        if not self.behavior_history:
            return
            
        # Calculate statistics
        classes = [b['class'] for b in self.behavior_history]
        
        # Count behavior types
        behavior_counts = {}
        for class_id, behavior_type in self.behavior_types.items():
            behavior_counts[behavior_type] = classes.count(class_id)
        
        # Calculate average confidence
        confidences = [b['confidence'] for b in self.behavior_history]
        avg_confidence = np.mean(confidences)
        
        # Determine dominant behavior
        dominant_class = max(set(classes), key=classes.count)
        dominant_behavior = self.behavior_types[dominant_class]
        
        print(f"\n--- Session Statistics ---")
        print(f"Total Samples: {self.sample_count}")
        print(f"Analyses: {self.analysis_count}")
        print(f"Dominant Behavior: {dominant_behavior}")
        print(f"Average Confidence: {avg_confidence:.3f}")
        print(f"Behavior Distribution:")
        for behavior, count in behavior_counts.items():
            percentage = (count / self.analysis_count) * 100
            print(f"  {behavior}: {count} ({percentage:.1f}%)")
    
    def save_analysis_summary(self):
        """Save analysis summary to JSON file."""
        if not self.behavior_history:
            return
            
        # Calculate final statistics
        classes = [b['class'] for b in self.behavior_history]
        confidences = [b['confidence'] for b in self.behavior_history]
        
        behavior_counts = {}
        for class_id, behavior_type in self.behavior_types.items():
            behavior_counts[behavior_type] = classes.count(class_id)
        
        avg_confidence = np.mean(confidences)
        dominant_class = max(set(classes), key=classes.count)
        dominant_behavior = self.behavior_types[dominant_class]
        
        summary = {
            'session_info': {
                'start_time': self.timestamp_buffer[0] if self.timestamp_buffer else None,
                'end_time': self.timestamp_buffer[-1] if self.timestamp_buffer else None,
                'total_samples': self.sample_count,
                'total_analyses': self.analysis_count,
                'sample_rate': self.sample_rate,
                'window_size': self.window_size
            },
            'behavior_analysis': {
                'dominant_behavior': dominant_behavior,
                'average_confidence': avg_confidence,
                'behavior_distribution': behavior_counts,
                'behavior_history': self.behavior_history[-50:]  # Last 50 analyses
            },
            'files_created': {
                'data_log': str(self.filename),
                'analysis_summary': str(self.analysis_filename)
            }
        }
        
        try:
            with open(self.analysis_filename, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"Analysis summary saved to {self.analysis_filename}")
        except Exception as e:
            print(f"Error saving analysis summary: {e}")
    
    def stop_logging(self):
        """Stop data logging and close files."""
        self.running = False
        if self.csv_file:
            self.csv_file.close()
            print(f"Stopped logging. Total samples: {self.sample_count}")
            print(f"Data saved to: {self.filename}")
        
        # Save analysis summary
        self.save_analysis_summary()

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to gracefully stop."""
    print("\nStopping integrated analysis...")
    global analyzer
    if analyzer:
        analyzer.stop_logging()
    sys.exit(0)

def main():
    """Main function to run the integrated analysis system."""
    parser = argparse.ArgumentParser(description='Integrated Driver Behavior Analysis')
    parser.add_argument('--output-dir', default='logs', 
                       help='Output directory for log files (default: logs)')
    parser.add_argument('--sample-rate', type=int, default=50,
                       help='Sampling rate in Hz (default: 50)')
    parser.add_argument('--window-size', type=int, default=50,
                       help='Analysis window size (default: 50)')
    parser.add_argument('--bus', type=int, default=1,
                       help='I2C bus number (default: 1)')
    parser.add_argument('--address', default='0x68',
                       help='I2C address (default: 0x68)')
    parser.add_argument('--model-path', default='models/driver_behavior_model.pkl',
                       help='Path to trained model')
    
    args = parser.parse_args()
    
    # Convert address to integer
    address = int(args.address, 16)
    
    # Initialize integrated analyzer
    global analyzer
    analyzer = IntegratedDriverAnalysis(
        output_dir=args.output_dir,
        sample_rate=args.sample_rate,
        window_size=args.window_size,
        model_path=args.model_path,
        bus=args.bus,
        address=address
    )
    
    # Initialize MPU6050
    print("Initializing MPU6050...")
    analyzer.initialize_mpu6050()
    
    if not analyzer.initialized:
        print("Failed to initialize MPU6050. Exiting.")
        return
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start logging
    analyzer.start_logging()
    
    if not analyzer.running:
        print("Failed to start logging. Exiting.")
        return
    
    print("Starting integrated driver behavior analysis...")
    print("This will log all sensor data and provide real-time behavior analysis")
    
    # Main analysis loop
    try:
        while analyzer.running:
            start_time = time.time()
            
            # Read sensor data
            sensor_data = analyzer.get_sensor_data()
            if sensor_data:
                # Analyze behavior
                analyzer.analyze_behavior(sensor_data)
                
                # Log data
                analyzer.log_data(sensor_data)
                
                # Print status
                analyzer.print_status()
            
            # Maintain sample rate
            elapsed = time.time() - start_time
            sleep_time = max(0, analyzer.sample_interval - elapsed)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        pass
    finally:
        analyzer.stop_logging()
        
        # Print final statistics
        print("\n" + "="*60)
        print("FINAL SESSION STATISTICS")
        print("="*60)
        analyzer.print_statistics()

if __name__ == "__main__":
    main()

