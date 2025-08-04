import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
    
    # Development mode - set to False for production
    DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE', 'False').lower() == 'true'
    
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Production settings
    if not DEVELOPMENT_MODE:
        # Disable debug mode
        DEBUG = False
        # Use environment variable for secret key
        SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
        
        # File upload settings
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
        
        # Logging settings
        LOG_LEVEL = 'INFO'
    else:
        # Development settings
        DEBUG = True
        SECRET_KEY = 'dev-secret-key'
        LOG_LEVEL = 'DEBUG'
