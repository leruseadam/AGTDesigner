# PythonAnywhere-specific configuration
import os

class PythonAnywhereConfig:
    """Configuration specific to PythonAnywhere environment."""
    
    # Server settings
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    
    # Logging settings
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/home/adamcordova/pythonanywhere.log'
    
    # Performance settings
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    CACHE_DURATION = 180  # 3 minutes
    SESSION_LIFETIME = 1800  # 30 minutes
    
    # File processing settings
    CHUNK_SIZE = 500
    LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB
    ENABLE_MEMORY_MONITORING = True
    FORCE_GARBAGE_COLLECTION = True
    
    # Database settings
    DATABASE_PATH = '/home/adamcordova/AGTDesigner/product_database.db'
    
    # Upload settings
    UPLOAD_FOLDER = '/home/adamcordova/AGTDesigner/uploads'
    MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25MB
    
    # Error handling
    SUPPRESS_ERRORS = True
    SAFE_LOGGING = True
    
    @classmethod
    def get_config(cls):
        """Get configuration as dictionary."""
        return {key: value for key, value in cls.__dict__.items() 
                if not key.startswith('_') and not callable(value)}

# Export configuration
PYTHONANYWHERE_CONFIG = PythonAnywhereConfig.get_config()
