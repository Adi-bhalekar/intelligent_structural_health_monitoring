#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(cmd, description):
    print(f"\n📦 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 ASSET HEALTH AI - SETUP SCRIPT")
    print("=" * 60)
    
    # Create directories
    print("\n📁 Creating directory structure...")
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    print("✅ Directories created")
    
    # Check Python version
    print(f"\n🐍 Python version: {sys.version}")
    
    # Install requirements
    requirements = [
        'flask==2.3.3',
        'pandas==2.0.3', 
        'numpy==1.24.3',
        'scikit-learn==1.3.0',
        'joblib==1.3.2'
    ]
    
    print("\n📦 Installing dependencies...")
    for package in requirements:
        run_command(f'pip install "{package}"', f'Installing {package}')
    
    # Create the other necessary files
    print("\n📝 Creating configuration files...")
    
    # Create requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    
    # Create a simple generate_dataset.py if it doesn't exist
    if not os.path.exists('generate_dataset.py'):
        generate_code = '''import pandas as pd
import numpy as np

# Generate sample training data
np.random.seed(42)
data = {
    'temperature': np.random.normal(380, 15, 100),
    'pressure': np.random.normal(18, 2, 100),
    'load': np.random.uniform(0.4, 0.8, 100),
    'vibration_mag': np.random.uniform(0.05, 0.25, 100),
    'ultrasonic_energy': np.random.uniform(500, 800, 100),
    'health': np.random.uniform(0.3, 1.0, 100),
    'failure_30d': np.random.binomial(1, 0.2, 100)
}
df = pd.DataFrame(data)
df.to_csv('data/training_data.csv', index=False)
print("✅ Sample training data created")
'''
        with open('generate_dataset.py', 'w') as f:
            f.write(generate_code)
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python generate_dataset.py")
    print("2. Run: python app.py")
    print("3. Open browser to: http://localhost:5000")
    print("=" * 60)

if __name__ == '__main__':
    main()