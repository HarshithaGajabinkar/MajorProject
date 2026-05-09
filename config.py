# config.py - UPDATED
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    MODEL_PATH = 'model/disease_model.pkl'
    LABEL_ENCODER_PATH = 'model/label_encoder.pkl'
    SYMPTOM_ENCODER_PATH = 'model/symptom_encoder.pkl'
    SEVERITY_DATA_PATH = 'data/disease_severity.csv'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google Maps Configuration (REQUIRED for maps)
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or 'YOUR_GOOGLE_MAPS_API_KEY_HERE'
    
    # Map settings
    DEFAULT_LOCATION = {
        'lat': 18.2046,  # Huzurabad latitude
        'lng': 79.4997   # Huzurabad longitude
    }
    
    # Hospital search settings
    DEFAULT_SEARCH_RADIUS = 5000  # meters
    MAX_HOSPITALS_TO_SHOW = 10