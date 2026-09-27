from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

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