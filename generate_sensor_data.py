import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sensor_data(num_samples=1000, include_anomalies=True, random_seed=42):
    """
    Generate synthetic sensor data for equipment monitoring
    
    Parameters:
    -----------
    num_samples : int
        Number of data samples to generate
    include_anomalies : bool
        Whether to include some anomalous readings
    random_seed : int
        Random seed for reproducibility
    
    Returns:
    --------
    pandas.DataFrame
        Generated sensor data
    """
    np.random.seed(random_seed)
    
    # Generate timestamps (every 10 minutes starting from now)
    start_time = datetime.now() - timedelta(days=30)
    timestamps = [start_time + timedelta(minutes=10*i) for i in range(num_samples)]
    
    # Base patterns (trends and cycles)
    time_points = np.arange(num_samples)
    
    # Temperature: increasing trend with daily cycles
    base_temp = 375 + 0.08 * time_points  # Slow upward drift
    daily_cycle = 5 * np.sin(2 * np.pi * time_points / 144)  # 144 samples per day (every 10 mins)
    temp_noise = np.random.normal(0, 1.5, num_samples)
    temperature = base_temp + daily_cycle + temp_noise
    
    # Pressure: increasing trend correlated with temperature
    base_pressure = 17.5 + 0.005 * time_points
    pressure_noise = np.random.normal(0, 0.1, num_samples)
    pressure = base_pressure + 0.03 * (temperature - 375) + pressure_noise
    
    # Load: varies with shift patterns
    load_cycles = 0.1 * np.sin(2 * np.pi * time_points / 72)  # 12-hour cycles
    load_trend = 0.55 + 0.00015 * time_points
    load_noise = np.random.normal(0, 0.02, num_samples)
    load = load_trend + load_cycles + load_noise
    load = np.clip(load, 0.45, 0.95)  # Keep within reasonable bounds
    
    # Vibrations: correlated with load and temperature
    vibration_base = 0.08 + 0.0001 * time_points
    vibration_x = vibration_base + 0.15 * (load - 0.55) + np.random.normal(0, 0.02, num_samples)
    vibration_y = vibration_base * 0.7 + 0.1 * (load - 0.55) + np.random.normal(0, 0.015, num_samples)
    
    # Ultrasonic measurements
    ultrasonic_trend = 40 + 0.015 * time_points
    ultrasonic_amplitude = ultrasonic_trend + 5 * np.sin(2 * np.pi * time_points / 288) + np.random.normal(0, 1.5, num_samples)
    ultrasonic_time = 12.0 + 0.0025 * time_points + np.random.normal(0, 0.15, num_samples)
    
    # Create DataFrame
    data = {
        'timestamp': timestamps,
        'time_index': time_points + 1,  # 1-based index
        'temperature': np.round(temperature, 1),
        'pressure': np.round(pressure, 1),
        'load': np.round(load, 2),
        'vibration_x': np.round(vibration_x, 2),
        'vibration_y': np.round(vibration_y, 2),
        'ultrasonic_amplitude': np.round(ultrasonic_amplitude, 0).astype(int),
        'ultrasonic_time': np.round(ultrasonic_time, 1),
    }
    
    df = pd.DataFrame(data)
    
    # Add some anomalies if requested
    if include_anomalies:
        df = add_anomalies(df)
    
    # Add derived features
    df = add_derived_features(df)
    
    return df

def add_anomalies(df, anomaly_rate=0.02):
    """
    Add realistic anomalies to the sensor data
    """
    df_anomalous = df.copy()
    num_samples = len(df)
    num_anomalies = int(anomaly_rate * num_samples)
    
    # Randomly select indices for anomalies
    anomaly_indices = np.random.choice(num_samples, num_anomalies, replace=False)
    
    for idx in anomaly_indices:
        anomaly_type = np.random.choice(['spike', 'drift', 'stuck', 'noise'])
        
        if anomaly_type == 'spike':
            # Random spike in one or more sensors
            sensor = np.random.choice(['temperature', 'pressure', 'vibration_x', 'vibration_y'])
            spike_size = np.random.uniform(10, 50) if sensor == 'temperature' else np.random.uniform(5, 20)
            df_anomalous.loc[idx, sensor] += spike_size
            
        elif anomaly_type == 'drift':
            # Gradual drift starting from this point
            drift_length = np.random.randint(5, 20)
            sensor = np.random.choice(['temperature', 'pressure'])
            drift_rate = np.random.uniform(0.5, 2.0) if sensor == 'temperature' else np.random.uniform(0.1, 0.5)
            
            for i in range(min(drift_length, num_samples - idx)):
                df_anomalous.loc[idx + i, sensor] += drift_rate * (i + 1)
                
        elif anomaly_type == 'stuck':
            # Stuck sensor value
            sensor = np.random.choice(['temperature', 'pressure', 'load'])
            df_anomalous.loc[idx:idx+np.random.randint(5, 15), sensor] = df_anomalous.loc[idx, sensor]
            
        elif anomaly_type == 'noise':
            # Increased noise
            sensor = np.random.choice(['vibration_x', 'vibration_y'])
            noise_level = np.random.uniform(0.1, 0.3)
            df_anomalous.loc[idx:idx+np.random.randint(3, 8), sensor] += np.random.normal(0, noise_level, 1)[0]
    
    return df_anomalous

def add_derived_features(df):
    """
    Add useful derived features
    """
    df = df.copy()
    
    # Time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['shift'] = pd.cut(df['hour'], 
                         bins=[0, 8, 16, 24], 
                         labels=['Night', 'Day', 'Evening'],
                         include_lowest=True)
    
    # Equipment health indicators
    df['temp_pressure_ratio'] = df['temperature'] / df['pressure']
    df['vibration_magnitude'] = np.sqrt(df['vibration_x']**2 + df['vibration_y']**2)
    df['load_efficiency'] = df['load'] / (df['temperature'] / 100)  # Simplified metric
    
    # Rate of change features
    df['temp_change_rate'] = df['temperature'].diff().fillna(0)
    df['pressure_change_rate'] = df['pressure'].diff().fillna(0)
    
    # Rolling statistics
    window_size = 6  # 1 hour window (6 * 10 minutes)
    df['temp_rolling_avg'] = df['temperature'].rolling(window=window_size, min_periods=1).mean()
    df['vibration_rolling_std'] = df['vibration_magnitude'].rolling(window=window_size, min_periods=1).std()
    
    return df

def generate_small_dataset():
    """Generate a small dataset like in the original example"""
    np.random.seed(42)
    
    data = {
        'time': list(range(1, 9)),
        'temperature': [380, 382, 385, 387, 390, 392, 395, 398],
        'pressure': [18.0, 18.3, 18.6, 18.9, 19.2, 19.5, 19.8, 20.1],
        'load': [0.60, 0.62, 0.65, 0.67, 0.70, 0.73, 0.76, 0.80],
        'vibration_x': [0.12, 0.13, 0.15, 0.16, 0.18, 0.20, 0.22, 0.25],
        'vibration_y': [0.08, 0.09, 0.10, 0.11, 0.12, 0.14, 0.15, 0.17],
        'ultrasonic_amplitude': [45, 46, 48, 50, 53, 55, 58, 62],
        'ultrasonic_time': [12.5, 12.7, 13.0, 13.3, 13.6, 13.9, 14.2, 14.5]
    }
    
    return pd.DataFrame(data)

def save_datasets():
    """Generate and save multiple datasets for different use cases"""
    
    # 1. Small example dataset (like original)
    small_df = generate_small_dataset()
    small_df.to_csv('sensor_data_small.csv', index=False)
    print(f"Small dataset saved: {len(small_df)} samples")
    
    # 2. Medium dataset for testing
    medium_df = generate_sensor_data(num_samples=1000, include_anomalies=True)
    medium_df.to_csv('sensor_data_medium.csv', index=False)
    print(f"Medium dataset saved: {len(medium_df)} samples")
    
    # 3. Large dataset for training models
    large_df = generate_sensor_data(num_samples=10000, include_anomalies=True)
    large_df.to_csv('sensor_data_large.csv', index=False)
    print(f"Large dataset saved: {len(large_df)} samples")
    
    # 4. Clean dataset (no anomalies) for baseline
    clean_df = generate_sensor_data(num_samples=1000, include_anomalies=False)
    clean_df.to_csv('sensor_data_clean.csv', index=False)
    print(f"Clean dataset saved: {len(clean_df)} samples")
    
    return small_df, medium_df, large_df, clean_df

# Example usage
if __name__ == "__main__":
    # Generate a sample dataset
    sensor_data = generate_sensor_data(num_samples=500, include_anomalies=True)
    
    # Display basic info
    print("Generated Sensor Data Sample:")
    print("=" * 80)
    print(f"Total samples: {len(sensor_data)}")
    print(f"Time range: {sensor_data['timestamp'].min()} to {sensor_data['timestamp'].max()}")
    print("\nFirst 5 rows:")
    print(sensor_data.head())
    
    print("\nStatistical Summary:")
    print(sensor_data[['temperature', 'pressure', 'load', 'vibration_x', 'vibration_y']].describe())
    
    # Save to CSV
    sensor_data.to_csv('generated_sensor_data.csv', index=False)
    print(f"\nData saved to 'generated_sensor_data.csv'")
    
    # Generate all datasets
    print("\n" + "="*80)
    print("Generating all datasets...")
    small, medium, large, clean = save_datasets()