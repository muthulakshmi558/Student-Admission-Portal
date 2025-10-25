import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///student_portal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'muthulakshmi5293@gmail.com'
    MAIL_PASSWORD = 'yourpassword'

    # Twilio Config
    TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_SID'
    TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'
    TWILIO_PHONE_NUMBER = '+1234567890'
