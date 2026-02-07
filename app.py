from flask import Flask, render_template, jsonify
import random
from datetime import datetime
import threading
import time
import os

app = Flask(__name__, static_folder='static')

# Global state
class AssetState:
    def __init__(self):
        self.health = 0.85
        self.fatigue = 0.12
        self.creep = 0.008
        self.corrosion = 0.15
        self.crack = 0.09
        self.temperature = 380
        self.pressure = 18.0
        self.load = 65.0
        self.vibration = 0.15
        self.ultrasonic_amp = 45.0
        self.ultrasonic_time = 13.0
        self.failure_prob = 0.15
        self.expected_cost = 1500000
        self.decision = "CONTINUE_OPERATION"
        self.decision_color = "success"
        self.is_monitoring = True
    
    def update(self):
        # Simulate sensor changes
        self.temperature = 380 + random.uniform(-10, 20)
        self.pressure = 18 + random.uniform(-1, 3)
        self.load = 60 + random.uniform(-10, 15)
        self.vibration = 0.1 + random.uniform(0, 0.2)
        self.ultrasonic_amp = 40 + random.uniform(0, 20)
        self.ultrasonic_time = 12 + random.uniform(0, 4)
        
        # Update damage slowly
        self.fatigue = min(0.5, self.fatigue + random.uniform(-0.005, 0.01))
        self.creep = min(0.02, self.creep + random.uniform(-0.0001, 0.0003))
        self.corrosion = min(0.3, self.corrosion + random.uniform(-0.002, 0.005))
        self.crack = min(0.4, self.crack + random.uniform(-0.003, 0.008))
        
        # Calculate health
        self.health = 1 - (0.3*self.fatigue + 0.25*self.creep + 0.2*self.corrosion + 0.25*self.crack)
        self.health = max(0.1, min(1.0, self.health))
        
        # Calculate failure probability
        self.failure_prob = (1 - self.health) * 0.8 + random.uniform(-0.05, 0.05)
        self.failure_prob = max(0.0, min(1.0, self.failure_prob))
        
        # Calculate expected cost
        self.expected_cost = self.failure_prob * 10000000
        
        # Make decision
        if self.expected_cost > 500000:
            self.decision = "IMMEDIATE_INSPECTION"
            self.decision_color = "danger"
        elif self.expected_cost > 2000000:
            self.decision = "SCHEDULE_REPAIR"
            self.decision_color = "warning"
        else:
            self.decision = "CONTINUE_OPERATION"
            self.decision_color = "success"
        
        return self.get_data()
    
    def get_data(self):
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'health': self.health,
            'health_percent': round(self.health * 100),
            'fatigue': self.fatigue,
            'creep': self.creep,
            'corrosion': self.corrosion,
            'crack': self.crack,
            'temperature': round(self.temperature, 1),
            'pressure': round(self.pressure, 1),
            'load': round(self.load, 1),
            'vibration': round(self.vibration, 3),
            'ultrasonic_amp': round(self.ultrasonic_amp, 1),
            'ultrasonic_time': round(self.ultrasonic_time, 1),
            'failure_prob': self.failure_prob,
            'failure_prob_percent': round(self.failure_prob * 100, 1),
            'expected_cost': int(self.expected_cost),
            'decision': self.decision,
            'decision_color': self.decision_color,
            'is_monitoring': self.is_monitoring
        }

# Create asset state
asset = AssetState()

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get current data"""
    data = asset.get_data()
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/update')
def update_data():
    """API endpoint to trigger an update"""
    data = asset.update()
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/start')
def start_monitoring():
    """Start monitoring"""
    asset.is_monitoring = True
    return jsonify({
        'status': 'success',
        'message': 'Monitoring started'
    })

@app.route('/api/stop')
def stop_monitoring():
    """Stop monitoring"""
    asset.is_monitoring = False
    return jsonify({
        'status': 'success', 
        'message': 'Monitoring stopped'
    })

@app.route('/api/reset')
def reset():
    """Reset to initial state"""
    global asset
    asset = AssetState()
    return jsonify({
        'status': 'success',
        'message': 'System reset'
    })

# Add a health check endpoint (REQUIRED for Render)
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Asset Health AI",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": "production"
    })

# Add error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Background update thread
def background_updater():
    """Background thread to update data periodically"""
    while True:
        if asset.is_monitoring:
            asset.update()
        time.sleep(2)  # Update every 2 seconds

# Start background thread
thread = threading.Thread(target=background_updater, daemon=True)
thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug MUST be False