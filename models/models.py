from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(250), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    documents = db.Column(db.String(250))  # file path
    photo = db.Column(db.String(250))      # photo path
    status = db.Column(db.String(20), default='Pending')  # Pending / Approved / Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
