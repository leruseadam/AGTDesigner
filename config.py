import os
from pathlib import Path

class Config:
    """Configuration class for the Label Maker application."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'label-maker-secret-key-2024-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    DEVELOPMENT_MODE = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # Session settings
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_MAX_SIZE = 8192  # Increased browser cookie size limit
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session lifetime
    SESSION_REFRESH_EACH_REQUEST = False  # Don't refresh session on every request
    SESSION_TYPE = 'filesystem'  # Use filesystem for session storage
    
    # Template settings
    TEMPLATES_AUTO_RELOAD = DEVELOPMENT_MODE
    SEND_FILE_MAX_AGE_DEFAULT = 0 if DEVELOPMENT_MODE else 31536000  # Cache static files for 1 year in production
    
    # Exception handling
    PROPAGATE_EXCEPTIONS = DEVELOPMENT_MODE
    
    # Testing
    TESTING = False
    
    # Performance settings
    DISABLE_STARTUP_FILE_LOADING = os.environ.get('DISABLE_STARTUP_FILE_LOADING', 'False').lower() == 'true'
    
    # Database configuration
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_database.db')
    
    # File upload configuration
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Template configuration
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
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