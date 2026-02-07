import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, confusion_matrix, classification_report
import joblib
import os

print("📊 Loading training data...")
df = pd.read_csv("data/training_data.csv")

# Feature engineering
df['ultrasonic_energy'] = df['ultrasonic_amplitude'] * df['ultrasonic_time']
df['load_var'] = 0.01  # Placeholder, will be calculated live

# Features for model
features = [
    'fatigue', 'creep', 'corrosion', 'crack_growth', 'health',
    'temperature', 'load', 'vibration_mag', 'ultrasonic_energy'
]

X = df[features]
y = df['failure_30d']

print(f"📈 Training on {len(X)} samples...")
print(f"   Features: {len(features)}")
print(f"   Failure cases: {y.sum()} ({y.mean():.2%})")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Train model
model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_prob)

print("\n✅ Model Training Complete!")
print(f"   ROC-AUC Score: {auc:.4f}")
print(f"   Accuracy: {(y_pred == y_test).mean():.4f}")

# Print confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\n📊 Confusion Matrix:")
print(f"   True Negatives:  {cm[0,0]}")
print(f"   False Positives: {cm[0,1]}")
print(f"   False Negatives: {cm[1,0]}")
print(f"   True Positives:  {cm[1,1]}")

# Save model
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/model.pkl')
print(f"\n💾 Model saved to: models/model.pkl")

# Save feature list
feature_info = {
    'features': features,
    'feature_importance': dict(zip(features, model.feature_importances_))
}
joblib.dump(feature_info, 'models/feature_info.pkl')

print("\n🎯 Ready for predictions!")