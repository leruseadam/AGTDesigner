import os
from pathlib import Path

class Config:
    """Configuration class for the Label Maker application."""
    
    # Development mode flag
    DEVELOPMENT_MODE = os.environ.get('FLASK_ENV') == 'development'
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    TESTING = False
    
    # Database configuration
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_database.db')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Template configuration
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Performance configuration
    LAZY_LOADING_ENABLED = True
    CACHE_DURATION = 300  # 5 minutes
    
    # Rate limiting
    RATE_LIMIT_WINDOW = 60  # 1 minute
    RATE_LIMIT_MAX_REQUESTS = 30  # Max requests per minute per IP
    
    # File processing
    TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    CLEANUP_INTERVAL = 3600  # 1 hour
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Default file configuration
    DEFAULT_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_products.xlsx')
    
    # PythonAnywhere specific settings
    PYTHONANYWHERE_MODE = os.environ.get('PYTHONANYWHERE_MODE', 'False').lower() == 'true'
    
    @classmethod
    def init_app(cls, app):
        """Initialize the app with this config."""
        # Create necessary directories
        for folder in [cls.UPLOAD_FOLDER, cls.TEMP_FOLDER]:
            Path(folder).mkdir(exist_ok=True)
        
        # Set Flask configuration
        app.config['SECRET_KEY'] = cls.SECRET_KEY
        app.config['DEBUG'] = cls.DEBUG
        app.config['TESTING'] = cls.TESTING
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        app.config['TEMPLATE_FOLDER'] = cls.TEMPLATE_FOLDER
        app.config['STATIC_FOLDER'] = cls.STATIC_FOLDER
        
        # Set cache configuration
        app.config['CACHE_TYPE'] = cls.CACHE_TYPE
        app.config['CACHE_DEFAULT_TIMEOUT'] = cls.CACHE_DEFAULT_TIMEOUT
        
        # Set session configuration
        app.config['SESSION_TYPE'] = cls.SESSION_TYPE
        app.config['PERMANENT_SESSION_LIFETIME'] = cls.PERMANENT_SESSION_LIFETIME
        
        return app

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DEVELOPMENT_MODE = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    DEVELOPMENT_MODE = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'label-maker-production-key-2024'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}