# 🚗 AI-Based Driver Behavior Analysis System

## 📚 Project Overview

The **AI-Based Driver Behavior Analysis System** is a comprehensive solution that combines real-time sensor data collection with machine learning to analyze and classify driver behavior patterns. The system uses MPU6050 IMU sensors to capture accelerometer and gyroscope data, processes it through a trained Random Forest model, and provides real-time feedback on driving behavior. It's designed to run on Raspberry Pi hardware for practical deployment in vehicles.

## 🌟 Features
- **📡 Real-time Sensor Data Collection:** Captures live accelerometer and gyroscope data from MPU6050 IMU sensors via I2C communication.

- **🧠 Machine Learning Classification:** Uses a trained Random Forest model (99.55% accuracy) to classify driving behavior into 4 categories: Normal, Moderate, Aggressive, and Dangerous driving.

- **⚡ Real-time Analysis:** Provides instant feedback on driving behavior with configurable confidence thresholds and sampling rates.

- **📊 Data Logging:** Comprehensive data logging system that saves sensor readings with timestamps for offline analysis.

- **🔄 Sliding Window Processing:** Implements advanced feature extraction using sliding windows to capture temporal patterns in driving behavior.

- **📈 Multiple Analysis Modes:** Supports both real-time inference and comprehensive offline analysis pipelines.

## 💻 Technologies Used
- **Programming Language:** 🐍 Python 3.11+
- **Hardware:** Raspberry Pi with MPU6050 IMU sensor
- **Communication:** I2C protocol for sensor communication
- **Machine Learning:** 
  - `🧠 scikit-learn` for Random Forest classification
  - `📦 ONNX Runtime` for optimized model inference
  - `💾 joblib` for model serialization
- **Data Processing:**
  - `📊 Pandas` for data manipulation and analysis
  - `🔢 NumPy` for numerical operations and array processing
  - `📈 Matplotlib` and `Seaborn` for data visualization
- **Real-time Processing:**
  - `📡 smbus` for I2C communication with MPU6050
  - `⏱️ collections.deque` for efficient sliding window operations
- **Model Export:** ONNX format for cross-platform deployment

## 📊 Data Source
The driving behavior data used in this project was obtained from the **Driving Behavior Dataset** by Yuksel, Asim Sinan; Atmaca, Şerafettin (2020), available at Mendeley Data.

### Citation:
> Yuksel, Asim Sinan; Atmaca, Şerafettin (2020), “Driving Behavior Dataset”, Mendeley Data, V2, doi: 10.17632/jj3tw8kj6h.2
 
## 📂 Project Structure

The project is organized for both real-time deployment and offline analysis:

```
├── Scripts/                    # Main application scripts
│   ├── real_time_imu.py        # Real-time behavior classification
│   ├── mpu6050_data_logger.py  # Sensor data logging
│   ├── integrated_driver_analysis.py  # Combined logging + analysis
│   └── analyze_driver_behavior.py     # Offline analysis pipeline
├── models/                     # Trained models and metadata
│   ├── driver_behavior_model.pkl      # Scikit-learn Random Forest model
│   ├── random_forest_model.onnx       # ONNX optimized model
│   └── feature_names.pkl             # Feature name mapping
├── datasets/                     # Data storage
│   └── features_14.csv        # Processed feature dataset
├── logs/                      # Runtime data logs
│   └── mpu6050_data_*.csv     # Sensor data recordings
├── visualizations/            # Generated charts and plots
├── reports/                   # Analysis reports
├── src/                      # Source code (if needed for development)
├── requirements.txt          # Python dependencies
├── MODEL_USAGE_GUIDE.md      # Model usage documentation
├── MPU6050_USAGE_GUIDE.md    # Hardware setup guide
└── README.md                 # This file
```


## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/driver-behavior-analysis.git
   cd driver-behavior-analysis
   ```

2. **Create a virtual environment:**

```bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install the required dependencies:**

```bash

pip install -r requirements.txt
```

## 🛠️ Usage

### Real-time Driver Behavior Analysis

#### 1. **Real-time Classification (Primary Use Case)**
```bash
# Run real-time behavior classification with MPU6050
python Scripts/real_time_imu.py

# Customize sampling rate and confidence threshold
python Scripts/real_time_imu.py --sample-rate 20 --threshold 0.70

# Use different I2C bus or address
python Scripts/real_time_imu.py --bus 1 --address 0x68
```

#### 2. **Data Logging**
```bash
# Log sensor data to CSV for offline analysis
python Scripts/mpu6050_data_logger.py

# Customize logging parameters
python Scripts/mpu6050_data_logger.py --sample-rate 50 --output-dir logs
```

#### 3. **Integrated Analysis (Logging + Real-time)**
```bash
# Combined data logging and real-time analysis
python Scripts/integrated_driver_analysis.py
```

### Offline Analysis Pipeline

#### 4. **Complete Analysis Pipeline**
```bash
# Run the complete offline analysis
python Scripts/analyze_driver_behavior.py

# Run specific analysis steps
python Scripts/analyze_driver_behavior.py --step preprocess
python Scripts/analyze_driver_behavior.py --step features
python Scripts/analyze_driver_behavior.py --step analyze
python Scripts/analyze_driver_behavior.py --step visualize
```

### Model Performance

The system includes a pre-trained Random Forest model with:
- **Accuracy:** 99.55%
- **Features:** 60 engineered features from sensor data
- **Classes:** 4 behavior types (Normal, Moderate, Aggressive, Dangerous)
- **Format:** Both scikit-learn (.pkl) and ONNX (.onnx) formats

### Output Files

After running the analysis, you'll find:

- **📊 Real-time Output:** Live behavior classification with timestamps
- **📈 Data Logs:** `logs/mpu6050_data_*.csv` - Raw sensor data recordings
- **🤖 Models:** `models/` - Trained machine learning models
- **📊 Visualizations:** `visualizations/` - Generated charts and plots
- **📋 Reports:** `reports/` - Analysis reports and summaries

## 🔧 Hardware Requirements

### Raspberry Pi Setup
- **Hardware:** Raspberry Pi 3B+ or newer
- **Sensor:** MPU6050 IMU sensor
- **Connections:** I2C communication (SDA/SCL pins)
- **Power:** 5V USB power supply
- **Storage:** MicroSD card (8GB+ recommended)

### MPU6050 Wiring
```
MPU6050    →    Raspberry Pi
VCC        →    3.3V
GND        →    GND
SCL        →    GPIO 3 (Pin 5)
SDA        →    GPIO 2 (Pin 3)
```

### Software Requirements
- **OS:** Raspberry Pi OS (latest)
- **Python:** 3.11+
- **I2C:** Enabled in raspi-config
- **Dependencies:** See `requirements.txt`

## 📊 System Architecture

The system operates in multiple modes:

1. **Real-time Mode:** Continuous sensor reading → Sliding window feature extraction → ML classification → Live feedback
2. **Logging Mode:** Continuous sensor reading → CSV data storage for offline analysis
3. **Integrated Mode:** Combines real-time analysis with data logging
4. **Offline Mode:** Batch processing of logged data for comprehensive analysis

## 🔮 Future Enhancements
- **📡 OBD-II Integration:** Connect to vehicle's OBD-II port for additional data
- **🧬 Deep Learning Models:** Implement LSTM/CNN for temporal pattern recognition
- **📱 Mobile App:** Real-time dashboard and historical analysis
- **☁️ Cloud Integration:** Upload data for fleet management and analytics
- **🔔 Alert System:** Real-time notifications for dangerous driving patterns

## 🤝 Contribution

Contributions to the project are welcome. If you have ideas or improvements, feel free to create an issue or submit a pull request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📬 Contact

For any questions or suggestions, please reach out to:

- **📧 Email:** raisunlakra18@gmail.com
- **💼 LinkedIn:** Raisun Lakra
- **🐱 GitHub:** RaisunLakra

