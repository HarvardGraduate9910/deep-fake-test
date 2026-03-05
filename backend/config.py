"""
Configuration Management for Deep Fake Detection Backend
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    
    # Detection
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
    MIN_FACE_SIZE = int(os.getenv('MIN_FACE_SIZE', 50))
    SAMPLING_RATE = int(os.getenv('SAMPLING_RATE', 5))
    DETECTION_METHOD = os.getenv('DETECTION_METHOD', 'ensemble')
    
    # Model
    USE_GPU = os.getenv('USE_GPU', 'True').lower() == 'true'
    MODEL_PATH = os.getenv('MODEL_PATH', './models/')
    PRETRAINED_MODEL = os.getenv('PRETRAINED_MODEL', 'faceforensics')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/detection.log')
    
    # Storage
    STORAGE_PATH = os.getenv('STORAGE_PATH', './storage/')
    ENABLE_FRAME_STORAGE = os.getenv('ENABLE_FRAME_STORAGE', 'False').lower() == 'true'
    RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', 7))
    
    # API
    MAX_FRAME_SIZE = 1024 * 1024 * 5  # 5MB
    REQUEST_TIMEOUT = 30  # seconds
    
    # Performance
    MAX_WORKERS = 4
    BATCH_SIZE = 32
    
    @staticmethod
    def init_app(app):
        """Initialize app with config"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    CONFIDENCE_THRESHOLD = 0.7  # Stricter for testing


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get current configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
