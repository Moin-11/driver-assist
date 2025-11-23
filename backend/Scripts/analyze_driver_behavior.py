#!/usr/bin/env python3
"""
Main Driver Behavior Analysis Script

This is the comprehensive entry point for the AI-Based Driver Behavior Analysis System.
It orchestrates the entire data processing and analysis pipeline, from raw sensor data
to trained machine learning models and visualizations.

Pipeline Overview:
1. Data Preprocessing: Clean and prepare raw sensor data
2. Feature Engineering: Extract statistical features from time-series data
3. Model Training: Train Random Forest classifier on engineered features
4. Analysis: Generate insights and performance metrics
5. Visualization: Create charts and reports for data interpretation

Key Features:
- Modular pipeline design for flexible execution
- Comprehensive data preprocessing and cleaning
- Advanced feature engineering with sliding windows
- Machine learning model training and evaluation
- Automated visualization generation
- Configurable execution steps

Usage Examples:
    # Run complete pipeline
    python analyze_driver_behavior.py
    
    # Run specific steps
    python analyze_driver_behavior.py --step preprocess
    python analyze_driver_behavior.py --step features
    python analyze_driver_behavior.py --step analyze
    python analyze_driver_behavior.py --step visualize

Author: Driver Behavior Analysis System
Version: 1.0
"""

# Standard library imports
import sys          # For system-specific parameters and functions
import os           # For operating system interface
from pathlib import Path  # For cross-platform path handling
import argparse     # For command-line argument parsing
import warnings     # For suppressing non-critical warnings

# Add src directory to Python path for module imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import analysis pipeline components
from scripts.data_preprocessing import DriverBehaviorDataProcessor
from scripts.feature_engineering import WindowFeatureEngineer, process_existing_features
from scripts.driver_behavior_analysis import DriverBehaviorAnalyzer
from scripts.visualization import DriverBehaviorVisualizer

# Suppress warnings for cleaner output during analysis
warnings.filterwarnings('ignore')

def setup_directories():
    """
    Create necessary directory structure for the analysis pipeline.
    
    This function ensures all required directories exist for the data processing
    pipeline. It creates directories for intermediate data, final results,
    trained models, visualizations, and analysis reports.
    
    Directory Structure:
    - datasets/silver: Intermediate processed data
    - datasets/gold: Final processed data ready for analysis
    - models: Trained machine learning models
    - visualizations: Generated charts and plots
    - reports: Analysis reports and summaries
    """
    # Define required directories for the analysis pipeline
    directories = [
        "datasets/silver",    # Intermediate processed data storage
        "datasets/gold",      # Final processed data storage
        "models",             # Trained model storage
        "visualizations",     # Generated visualization storage
        "reports"            # Analysis report storage
    ]
    
    # Create directories with parent creation enabled
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def run_data_preprocessing():
    """
    Execute the data preprocessing pipeline.
    
    This function handles the first stage of the analysis pipeline, which includes:
    - Loading raw sensor data from CSV files
    - Data cleaning and validation
    - Handling missing values and outliers
    - Data type conversion and standardization
    - Saving processed data for subsequent steps
    
    Returns:
        pd.DataFrame: Cleaned and processed sensor data ready for feature engineering
    """
    print("\n" + "="*60)
    print("STEP 1: DATA PREPROCESSING")
    print("="*60)
    
    # Define input and output paths for data processing
    raw_data_path = "src/datasets/bronze/Driving Behavior Dataset/sensor_raw.csv"
    output_path = "datasets/silver/processed_driver_behavior_data.csv"
    
    # Initialize data processor with raw data path
    processor = DriverBehaviorDataProcessor(raw_data_path)
    
    # Process raw data through cleaning and validation pipeline
    processed_df = processor.process_data()
    
    # Save processed data to intermediate storage for next pipeline step
    processor.save_processed_data(output_path)
    
    return processed_df

def run_feature_engineering():
    """Run feature engineering pipeline."""
    print("\n" + "="*60)
    print("STEP 2: FEATURE ENGINEERING")
    print("="*60)
    
    # Process existing pre-computed features
    process_existing_features()
    
    # Additional feature engineering on raw data
    raw_data_path = "src/datasets/bronze/Driving Behavior Dataset/sensor_raw.csv"
    
    # Load raw data
    import pandas as pd
    df_raw = pd.read_csv(raw_data_path)
    
    # Create window-based features
    engineer = WindowFeatureEngineer(window_sizes=[5, 10, 15, 20])
    features_df = engineer.create_window_features(df_raw)
    
    # Save features
    features_output_path = "datasets/silver/window_features.csv"
    engineer.save_features(features_df, features_output_path)
    
    return features_df

def run_analysis():
    """Run driver behavior analysis."""
    print("\n" + "="*60)
    print("STEP 3: DRIVER BEHAVIOR ANALYSIS")
    print("="*60)
    
    # Try to use processed data first, then raw data
    data_paths = [
        "datasets/silver/processed_driver_behavior_data.csv",
        "src/datasets/bronze/Driving Behavior Dataset/sensor_raw.csv"
    ]
    
    data_path = None
    for path in data_paths:
        if Path(path).exists():
            data_path = path
            break
    
    if data_path is None:
        print("No data found! Please check your data paths.")
        return
    
    analyzer = DriverBehaviorAnalyzer(data_path)
    analyzer.load_data()
    analyzer.prepare_data()
    analyzer.train_models()
    analyzer.evaluate_models()
    analyzer.analyze_driver_behavior()
    
    # Generate visualizations
    analyzer.plot_model_comparison()
    analyzer.plot_feature_importance()
    analyzer.plot_confusion_matrix()
    
    # Save best model
    if analyzer.results:
        best_model_name = max(analyzer.results.items(), key=lambda x: x[1]['accuracy'])[0]
        analyzer.save_model(best_model_name, f"models/{best_model_name.lower().replace(' ', '_')}_model.pkl")
    
    # Generate report
    analyzer.generate_report("reports/driver_behavior_analysis_report.txt")
    
    return analyzer

def run_visualization():
    """Run visualization pipeline."""
    print("\n" + "="*60)
    print("STEP 4: DATA VISUALIZATION")
    print("="*60)
    
    # Try to use processed data first, then raw data
    data_paths = [
        "datasets/silver/processed_driver_behavior_data.csv",
        "src/datasets/bronze/Driving Behavior Dataset/sensor_raw.csv"
    ]
    
    data_path = None
    for path in data_paths:
        if Path(path).exists():
            data_path = path
            break
    
    if data_path is None:
        print("No data found! Please check your data paths.")
        return
    
    visualizer = DriverBehaviorVisualizer(data_path)
    visualizer.load_data()
    visualizer.generate_all_visualizations()
    
    return visualizer

def main():
    """Main function to run the complete pipeline."""
    parser = argparse.ArgumentParser(description='AI-Based Driver Behavior Analysis System')
    parser.add_argument('--step', choices=['preprocess', 'features', 'analyze', 'visualize', 'all'], 
                       default='all', help='Which step to run')
    parser.add_argument('--data-path', type=str, 
                       default='src/datasets/bronze/Driving Behavior Dataset/sensor_raw.csv',
                       help='Path to the raw data')
    
    args = parser.parse_args()
    
    print("🚗 AI-Based Driver Behavior Analysis System")
    print("=" * 60)
    
    # Setup directories
    setup_directories()
    
    try:
        if args.step in ['preprocess', 'all']:
            run_data_preprocessing()
        
        if args.step in ['features', 'all']:
            run_feature_engineering()
        
        if args.step in ['analyze', 'all']:
            run_analysis()
        
        if args.step in ['visualize', 'all']:
            run_visualization()
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nGenerated files:")
        print("📊 Visualizations: visualizations/")
        print("📈 Reports: reports/")
        print("🤖 Models: models/")
        print("💾 Processed Data: datasets/silver/")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("Please check your data paths and dependencies.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())





