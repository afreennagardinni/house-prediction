from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///house_price.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy=True)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    area = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    stories = db.Column(db.Integer, nullable=False)
    mainroad = db.Column(db.String(10), nullable=False)
    guestroom = db.Column(db.String(10), nullable=False)
    basement = db.Column(db.String(10), nullable=False)
    hotwaterheating = db.Column(db.String(10), nullable=False)
    airconditioning = db.Column(db.String(10), nullable=False)
    parking = db.Column(db.Integer, nullable=False)
    prefarea = db.Column(db.String(10), nullable=False)
    furnishingstatus = db.Column(db.String(20), nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load model files
print("\nLoading model files...")
try:
    model = joblib.load('house_price_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoders = joblib.load('label_encoders.pkl')
    feature_columns = joblib.load('feature_columns.pkl')
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("Please run check_and_train.py first")
    model = None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.prediction_date.desc()).all()
    stats = {
        'total_predictions': len(predictions),
        'avg_price': np.mean([p.predicted_price for p in predictions]) if predictions else 0,
        'max_price': max([p.predicted_price for p in predictions]) if predictions else 0,
        'min_price': min([p.predicted_price for p in predictions]) if predictions else 0
    }
    return render_template('dashboard.html', predictions=predictions, stats=stats)

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        try:
            # Get form data
            area = float(request.form['area'])
            bedrooms = int(request.form['bedrooms'])
            bathrooms = int(request.form['bathrooms'])
            stories = int(request.form['stories'])
            mainroad = request.form['mainroad']
            guestroom = request.form['guestroom']
            basement = request.form['basement']
            hotwaterheating = request.form['hotwaterheating']
            airconditioning = request.form['airconditioning']
            parking = int(request.form['parking'])
            prefarea = request.form['prefarea']
            furnishingstatus = request.form['furnishingstatus']
            
            # Create feature array
            # Map categorical values
            def map_yes_no(value):
                return 1 if value == 'yes' else 0
            
            def map_furnishing(value):
                if value == 'furnished':
                    return 2
                elif value == 'semi-furnished':
                    return 1
                else:
                    return 0
            
            # Create features in the correct order
            features = np.array([[
                area,
                bedrooms,
                bathrooms,
                stories,
                map_yes_no(mainroad),
                map_yes_no(guestroom),
                map_yes_no(basement),
                map_yes_no(hotwaterheating),
                map_yes_no(airconditioning),
                parking,
                map_yes_no(prefarea),
                map_furnishing(furnishingstatus)
            ]])
            
            # Scale features
            features_scaled = scaler.transform(features)
            
            # Make prediction
            prediction = model.predict(features_scaled)[0]
            
            # Save to database
            new_prediction = Prediction(
                user_id=current_user.id,
                area=area,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                stories=stories,
                mainroad=mainroad,
                guestroom=guestroom,
                basement=basement,
                hotwaterheating=hotwaterheating,
                airconditioning=airconditioning,
                parking=parking,
                prefarea=prefarea,
                furnishingstatus=furnishingstatus,
                predicted_price=prediction
            )
            db.session.add(new_prediction)
            db.session.commit()
            
            flash(f'✅ Predicted House Price: ₹{prediction:,.2f}', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'❌ Error making prediction: {str(e)}', 'danger')
            return redirect(url_for('predict'))
    
    return render_template('predict.html')

@app.route('/delete_prediction/<int:pred_id>')
@login_required
def delete_prediction(pred_id):
    prediction = Prediction.query.get_or_404(pred_id)
    if prediction.user_id == current_user.id:
        db.session.delete(prediction)
        db.session.commit()
        flash('Prediction deleted successfully', 'success')
    else:
        flash('Unauthorized', 'danger')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("\n✅ Database created successfully!")
    print("\n" + "="*50)
    print("🚀 Server starting at: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)