# Upload Performance Configuration
# This file contains settings to optimize file upload performance

# Enable ultra-fast upload mode
ENABLE_ULTRA_FAST_UPLOAD = True

# Enable background processing
ENABLE_BACKGROUND_PROCESSING = True

# Enable minimal processing during upload
ENABLE_MINIMAL_PROCESSING = True

# Enable chunked reading for large files
ENABLE_CHUNKED_READING = True

# File size thresholds (in MB)
CHUNKED_READING_THRESHOLD = 10
LARGE_FILE_THRESHOLD = 50

# Memory optimization settings
ENABLE_MEMORY_OPTIMIZATION = True
FORCE_GARBAGE_COLLECTION = True

# Cache optimization
ENABLE_SMART_CACHING = True
MAX_CACHE_SIZE = 3

# PythonAnywhere specific optimizations
ENABLE_PYTHONANYWHERE_MODE = True
DISABLE_HEAVY_FEATURES = True

# Upload timeout settings (in seconds)
UPLOAD_TIMEOUT = 300
BACKGROUND_PROCESSING_TIMEOUT = 600

# Logging level for performance monitoring
PERFORMANCE_LOGGING_LEVEL = "INFO"
