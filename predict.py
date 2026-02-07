import pandas as pd
import numpy as np
import joblib
from datetime import datetime

class AssetHealthPredictor:
    def __init__(self):
        # Load model
        self.model = joblib.load('models/model.pkl')
        self.features = joblib.load('models/feature_info.pkl')['features']
        
        # Initialize damage state
        self.fatigue = 0.0
        self.creep = 0.0
        self.corrosion = 0.0
        self.crack = 0.0
        self.prev_load = None
        
        # Cost parameters
        self.inspection_cost = 500000  # ₹
        self.repair_cost = 2000000     # ₹
        self.failure_cost = 10000000   # ₹
        
    def update_damage(self, sensor_data):
        """Update damage metrics based on sensor readings"""
        if self.prev_load is None:
            self.prev_load = sensor_data['load']
            
        # Calculate vibration magnitude
        vibration_mag = np.sqrt(sensor_data['vibration_x']**2 + 
                               sensor_data['vibration_y']**2)
        
        # Update damage
        self.fatigue += 0.02 * abs(sensor_data['load'] - self.prev_load) + 0.01 * vibration_mag
        self.creep += 0.00001 * sensor_data['temperature']
        self.corrosion += 0.001
        self.crack += 0.0005 * sensor_data['ultrasonic_amplitude'] + 0.001 * sensor_data['ultrasonic_time']
        
        self.prev_load = sensor_data['load']
        
        # Calculate health
        health = 1 - (0.3*self.fatigue + 0.25*self.creep + 0.2*self.corrosion + 0.25*self.crack)
        health = max(0.0, min(1.0, health))
        
        return health, vibration_mag
    
    def predict(self, sensor_data):
        """Make prediction for current sensor data"""
        # Update damage and get health
        health, vibration_mag = self.update_damage(sensor_data)
        
        # Calculate features
        ultrasonic_energy = sensor_data['ultrasonic_amplitude'] * sensor_data['ultrasonic_time']
        
        # Create feature vector
        features = pd.DataFrame([[
            self.fatigue,
            self.creep,
            self.corrosion,
            self.crack,
            health,
            sensor_data['temperature'],
            sensor_data['load'],
            vibration_mag,
            ultrasonic_energy
        ]], columns=self.features)
        
        # Make prediction
        failure_prob = self.model.predict_proba(features)[0, 1]
        expected_cost = failure_prob * self.failure_cost
        
        # Make decision
        if expected_cost > self.inspection_cost:
            decision = "IMMEDIATE_INSPECTION"
            action = "Schedule immediate inspection and prepare for shutdown"
            color = "danger"
        elif expected_cost > self.repair_cost:
            decision = "SCHEDULE_REPAIR"
            action = "Plan repair during next maintenance window"
            color = "warning"
        else:
            decision = "CONTINUE_OPERATION"
            action = "Continue normal operation with routine monitoring"
            color = "success"
        
        return {
            'health': health,
            'failure_probability': failure_prob,
            'decision': decision,
            'action': action,
            'color': color,
            'damage_metrics': {
                'fatigue': self.fatigue,
                'creep': self.creep,
                'corrosion': self.corrosion,
                'crack': self.crack
            },
            'expected_cost': expected_cost,
            'vibration_magnitude': vibration_mag,
            'ultrasonic_energy': ultrasonic_energy,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def reset(self):
        """Reset damage state"""
        self.fatigue = 0.0
        self.creep = 0.0
        self.corrosion = 0.0
        self.crack = 0.0
        self.prev_load = None

def main():
    """Test prediction with sample data"""
    print("🧠 Testing Asset Health Prediction System\n")
    
    # Create predictor
    predictor = AssetHealthPredictor()
    
    # Sample sensor data
    sample_data = {
        'temperature': 385,
        'pressure': 18.6,
        'load': 0.65,
        'vibration_x': 0.15,
        'vibration_y': 0.10,
        'ultrasonic_amplitude': 48,
        'ultrasonic_time': 13.0
    }
    
    # Make prediction
    result = predictor.predict(sample_data)
    
    # Display results
    print("📊 PREDICTION RESULTS:")
    print("-" * 50)
    print(f"Health Score:           {result['health']:.3f}")
    print(f"Failure Probability:    {result['failure_probability']:.1%}")
    print(f"Expected Cost:         ₹{result['expected_cost']:,.0f}")
    print(f"\nDecision:              {result['decision']}")
    print(f"Action:                {result['action']}")
    print(f"\nDamage Metrics:")
    print(f"  Fatigue:             {result['damage_metrics']['fatigue']:.4f}")
    print(f"  Creep:               {result['damage_metrics']['creep']:.6f}")
    print(f"  Corrosion:           {result['damage_metrics']['corrosion']:.4f}")
    print(f"  Crack Growth:        {result['damage_metrics']['crack']:.4f}")
    print("-" * 50)

if __name__ == "__main__":
    main()