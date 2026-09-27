import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import joblib

print("="*50)
print("Checking and Training Model")
print("="*50)

# Check if housing.csv exists
if not os.path.exists('housing.csv'):
    print("\n❌ ERROR: housing.csv not found!")
    print("Please download housing.csv from Kaggle and place it here.")
    exit(1)

print("\n✓ housing.csv found")

# Load and train model
print("\nLoading dataset...")
df = pd.read_csv('housing.csv')
print(f"✓ Loaded {len(df)} rows")

# Encode categorical variables
categorical_cols = ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 
                   'airconditioning', 'prefarea', 'furnishingstatus']

label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Prepare features
X = df.drop('price', axis=1)
y = df['price']

# Split and scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train model
print("\nTraining Random Forest model...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Save everything
print("\nSaving model files...")
joblib.dump(model, 'house_price_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')
joblib.dump(X.columns.tolist(), 'feature_columns.pkl')

print("\n✅ Model training complete!")
print("Files saved:")
print("  - house_price_model.pkl")
print("  - scaler.pkl")
print("  - label_encoders.pkl")
print("  - feature_columns.pkl")