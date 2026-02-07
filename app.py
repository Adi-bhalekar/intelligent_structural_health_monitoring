from flask import Flask, render_template, jsonify
import random
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)

# Simplified AssetState without pandas
class AssetState:
    def __init__(self):
        self.health = 0.85
        self.fatigue = 0.12
        self.creep = 0.008
        self.corrosion = 0.15
        self.crack = 0.09
        self.is_monitoring = True
    
    def generate_sensor_data(self):
        """Generate simulated sensor data"""
        return {
            'temperature': round(380 + random.uniform(-10, 20), 1),
            'pressure': round(18 + random.uniform(-1, 3), 1),
            'load': round(60 + random.uniform(-10, 15), 1),
            'vibration': round(0.1 + random.uniform(0, 0.2), 3),
            'ultrasonic_amp': round(45 + random.uniform(0, 20), 1),
            'ultrasonic_time': round(13 + random.uniform(0, 4), 1)
        }
    
    def update(self):
        """Update damage metrics"""
        # Simulate gradual damage
        self.fatigue = min(0.5, self.fatigue + random.uniform(-0.002, 0.005))
        self.creep = min(0.02, self.creep + random.uniform(-0.0001, 0.0003))
        self.corrosion = min(0.3, self.corrosion + random.uniform(-0.001, 0.003))
        self.crack = min(0.4, self.crack + random.uniform(-0.002, 0.006))
        
        # Calculate health
        self.health = 1 - (0.3*self.fatigue + 0.25*self.creep + 0.2*self.corrosion + 0.25*self.crack)
        self.health = max(0.1, min(1.0, self.health))
        
        # Calculate failure probability
        failure_prob = (1 - self.health) * 0.8 + random.uniform(-0.03, 0.03)
        failure_prob = max(0.0, min(1.0, failure_prob))
        
        # Calculate expected cost
        expected_cost = failure_prob * 10000000
        
        # Make decision
        if expected_cost > 500000:
            decision = "IMMEDIATE_INSPECTION"
            color = "danger"
        elif expected_cost > 2000000:
            decision = "SCHEDULE_REPAIR"
            color = "warning"
        else:
            decision = "CONTINUE_OPERATION"
            color = "success"
        
        sensor_data = self.generate_sensor_data()
        
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'health': self.health,
            'health_percent': round(self.health * 100),
            'fatigue': self.fatigue,
            'creep': self.creep,
            'corrosion': self.corrosion,
            'crack': self.crack,
            'failure_prob': failure_prob,
            'failure_prob_percent': round(failure_prob * 100, 1),
            'expected_cost': int(expected_cost),
            'decision': decision,
            'decision_color': color,
            'sensor_data': sensor_data
        }
    
    def get_data(self):
        sensor_data = self.generate_sensor_data()
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'health': self.health,
            'health_percent': round(self.health * 100),
            'fatigue': self.fatigue,
            'creep': self.creep,
            'corrosion': self.corrosion,
            'crack': self.crack,
            'failure_prob': 0.15,
            'failure_prob_percent': 15.0,
            'expected_cost': 1500000,
            'decision': "CONTINUE_OPERATION",
            'decision_color': "success",
            'sensor_data': sensor_data
        }

# Initialize asset
asset = AssetState()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    data = asset.get_data()
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/update')
def update_data():
    data = asset.update()
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Asset Health AI",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": "production"
    })

# Background update thread
def background_updater():
    while True:
        if asset.is_monitoring:
            asset.update()
        time.sleep(2)

thread = threading.Thread(target=background_updater, daemon=True)
thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Asset Health AI on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
