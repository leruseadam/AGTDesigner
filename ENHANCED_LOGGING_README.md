# 🔍 Enhanced Logging System

This enhanced logging system makes web error logs much easier to read and debug.

## Features

### 🎨 **Color-Coded Logs**
- **🚨 Errors**: Red with detailed traceback information
- **⚠️ Warnings**: Yellow with context information  
- **ℹ️ Info**: Green with clean formatting
- **🔍 Debug**: Cyan for development debugging

### 📊 **Structured Logging**
- **Timestamp**: Precise timing with milliseconds
- **Location**: File, line number, and function name
- **Context**: Additional metadata for debugging
- **Categories**: Organized by component (routes, database, file processing)

### 🛠️ **Multiple Viewing Options**

#### 1. **Command Line Tool** (`log_viewer.py`)
```bash
# Show recent errors
python log_viewer.py --level ERROR --hours 24

# Show warnings
python log_viewer.py --level WARNING --hours 6

# Search for specific terms
python log_viewer.py --search "database" --hours 24

# Show statistics
python log_viewer.py --stats --hours 24

# Show last 20 lines
python log_viewer.py --tail 20
```

#### 2. **Web Interface** (`/logs`)
- Real-time log monitoring
- Filter by time range, level, and search terms
- Auto-refresh every 5 seconds
- Statistics dashboard
- Responsive design

#### 3. **Log Files**
- `logs/errors.log` - Error-only log file
- `logs/app.log` - General application log
- `logs/label_maker.log` - Legacy log format

## Usage

### In Your Code

```python
from enhanced_logging import EnhancedLogger, ErrorContext, log_route_error

# Create a logger
logger = EnhancedLogger("my_component")

# Log with context
logger.log_info("Processing started", {'file': 'data.xlsx', 'rows': 1000})

# Log errors with full context
try:
    # Some operation
    pass
except Exception as e:
    logger.log_error("Operation failed", e, {'user_id': 123, 'action': 'upload'})

# Use context manager for operations
with ErrorContext(logger, "file_processing", filename="data.xlsx"):
    # Your code here
    pass
```

### Route Error Logging

```python
@app.route('/api/my-endpoint')
def my_endpoint():
    try:
        # Your route logic
        pass
    except Exception as e:
        log_route_error('my_endpoint', e, request)
        return jsonify({'error': str(e)}), 500
```

## Log Format Examples

### Enhanced Format (New)
```
🚨 ERROR    [19:57:46.873] routes
   📍 app.py:1234 in get_filter_options()
   💬 Route error in get_filter_options | Context: method=POST | url=/api/filter-options
   Exception: ValueError: Invalid data format
   Traceback: Traceback (most recent call last):
     File "app.py", line 1234, in get_filter_options
       raise ValueError("Invalid data format")
   ValueError: Invalid data format
```

### Legacy Format (Still Supported)
```
2025-10-23 19:57:46 - routes - ERROR - Route error in get_filter_options
```

## Benefits

### 🚀 **Faster Debugging**
- **Color coding** makes errors stand out immediately
- **Structured format** provides all context at a glance
- **Search functionality** helps find specific issues quickly

### 📈 **Better Monitoring**
- **Real-time web interface** for live monitoring
- **Statistics dashboard** shows error trends
- **Filtering options** focus on relevant logs

### 🔧 **Easier Maintenance**
- **Context information** helps understand what was happening
- **Traceback details** pinpoint exact error locations
- **Multiple viewing options** suit different workflows

## Configuration

The enhanced logging system automatically:
- ✅ Detects if it's available and falls back to basic logging
- ✅ Creates log directories if they don't exist
- ✅ Suppresses noisy third-party library logs
- ✅ Formats logs consistently across the application

## Quick Start

1. **View logs in terminal:**
   ```bash
   python log_viewer.py --level ERROR --hours 1
   ```

2. **Open web interface:**
   - Navigate to `http://localhost:8001/logs`
   - Use filters to find specific issues
   - Monitor real-time logs

3. **Check log files:**
   ```bash
   tail -f logs/errors.log
   ```

## Troubleshooting

### If enhanced logging isn't working:
- Check that `enhanced_logging.py` is in the project root
- Verify the `logs/` directory exists and is writable
- The system will automatically fall back to basic logging

### If web interface shows no logs:
- Check that log files exist in the `logs/` directory
- Verify the time range filter isn't too restrictive
- Try refreshing the page

### For performance:
- Log files are automatically rotated
- Web interface limits to 100 most recent entries
- Command line tool can handle larger datasets
