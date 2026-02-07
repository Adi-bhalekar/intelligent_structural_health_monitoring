import numpy as np
import pandas as pd
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

np.random.seed(42)

# Number of samples
ROWS = 2000

fatigue = creep = corrosion = crack = 0.0
prev_load = 0.6
rows = []

for _ in range(ROWS):
    # Sensor readings
    temperature = np.random.normal(380, 15)
    pressure = np.random.normal(18, 2)
    load = np.clip(np.random.normal(0.65, 0.15), 0.1, 0.9)
    vibration_x = np.random.normal(0.15, 0.05)
    vibration_y = np.random.normal(0.10, 0.03)
    ultrasonic_amp = np.random.normal(50, 10)
    ultrasonic_time = np.random.normal(13, 1)
    
    # Calculate vibration magnitude
    vibration_mag = np.sqrt(vibration_x**2 + vibration_y**2)
    
    # Damage accumulation
    fatigue += 0.02 * abs(load - prev_load) + 0.01 * vibration_mag
    creep += 0.00001 * temperature
    corrosion += 0.001
    crack += 0.0005 * ultrasonic_amp + 0.001 * ultrasonic_time
    
    # Health calculation
    health = 1 - (0.3*fatigue + 0.25*creep + 0.2*corrosion + 0.25*crack)
    health = max(0.0, min(1.0, health))
    
    # Failure label (30-day prediction)
    failure_30d = 1 if health < 0.35 else 0
    
    rows.append([
        temperature, pressure, load,
        vibration_x, vibration_y, vibration_mag,
        ultrasonic_amp, ultrasonic_time,
        fatigue, creep, corrosion, crack,
        health, failure_30d
    ])
    
    prev_load = load

# Create DataFrame
df = pd.DataFrame(rows, columns=[
    "temperature", "pressure", "load",
    "vibration_x", "vibration_y", "vibration_mag",
    "ultrasonic_amplitude", "ultrasonic_time",
    "fatigue", "creep", "corrosion", "crack_growth",
    "health", "failure_30d"
])

# Save to CSV
df.to_csv("data/training_data.csv", index=False)
print("✅ Dataset generated successfully!")
print(f"   Rows: {len(df)}")
print(f"   Features: {len(df.columns)}")
print(f"   Failure rate: {df['failure_30d'].mean():.2%}")
print(f"   Saved to: data/training_data.csv")