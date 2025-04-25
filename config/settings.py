import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    TESTING = False
    
    # Email verification (set to False for development)
    REQUIRE_EMAIL_VERIFICATION = os.environ.get('REQUIRE_EMAIL_VERIFICATION', 'False').lower() == 'true'
    
    # Database settings - MySQL configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://username:password@localhost/smart_parking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Log SQL queries (for development)
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Admin settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    
    # Parking system settings
    BOOKING_EXPIRY_MINUTES = int(os.environ.get('BOOKING_EXPIRY_MINUTES') or 30)
    DEFAULT_HOURLY_RATE = float(os.environ.get('DEFAULT_HOURLY_RATE') or 5.0)
    PEAK_HOURS_RATE_MULTIPLIER = float(os.environ.get('PEAK_HOURS_RATE_MULTIPLIER') or 1.5)
    
    # Payment gateway settings
    PAYMENT_GATEWAY_API_KEY = os.environ.get('PAYMENT_GATEWAY_API_KEY')
    PAYMENT_GATEWAY_SECRET = os.environ.get('PAYMENT_GATEWAY_SECRET')
    
    # RFID and license plate recognition settings
    ENABLE_RFID = os.environ.get('ENABLE_RFID', 'False').lower() == 'true'
    ENABLE_LICENSE_PLATE_RECOGNITION = os.environ.get('ENABLE_LICENSE_PLATE_RECOGNITION', 'False').lower() == 'true'
    
    # ML model settings
    ML_MODEL_PATH = os.environ.get('ML_MODEL_PATH') or os.path.join(basedir, 'app/ml/models')
    
    # API settings
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT') or '100 per minute'
