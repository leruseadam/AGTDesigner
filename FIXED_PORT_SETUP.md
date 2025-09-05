# Fixed Port Setup for Label Maker

## Problem Solved
The Label Maker app was restarting on different ports due to:
1. **Development mode enabled** - causing auto-restarting when files change
2. **Multiple startup scripts** using different ports (5001, 5002, 5014)
3. **Dynamic port allocation** in some startup scripts

## Solution Implemented

### 1. Fixed Configuration (`config.py`)
- `DEVELOPMENT_MODE = False` - prevents auto-restarting
- `DEBUG = False` - improves production stability
- `TEMPLATES_AUTO_RELOAD = False` - prevents template reloading
- `SEND_FILE_MAX_AGE_DEFAULT = 31536000` - enables static file caching

### 2. Consistent Port Usage
- **Fixed Port**: 5014 (used across all startup scripts)
- **Fixed Host**: 127.0.0.1
- **No more port changes** - app stays on the same port

### 3. Updated Startup Scripts
All startup scripts now use the same configuration:

#### `start_app_fixed.py` (Recommended)
```bash
python start_app_fixed.py
```
- Sets port 5014
- Disables development mode
- Provides clear startup information

#### `run_app.sh`
```bash
./run_app.sh
```
- Bash script with virtual environment activation
- Sets port 5014 and disables development mode

#### `restart_app.py`
```bash
python restart_app.py
```
- Kills existing processes
- Starts fresh on port 5014

#### `fix_app_port.py`
```bash
python fix_app_port.py
```
- Sets environment variables for consistent behavior
- Use before running `python app.py`

## How to Use

### Option 1: Use the Fixed Startup Script (Recommended)
```bash
python start_app_fixed.py
```

### Option 2: Use the Shell Script
```bash
chmod +x run_app.sh
./run_app.sh
```

### Option 3: Manual Startup
```bash
export FLASK_PORT=5014
export HOST=127.0.0.1
export DEVELOPMENT_MODE=false
export DEBUG=false
python app.py
```

## Benefits

✅ **No more port changes** - app stays on port 5014  
✅ **No auto-restarting** - development mode disabled  
✅ **Consistent behavior** - all startup methods use same config  
✅ **Production stability** - debug mode disabled  
✅ **Better performance** - static file caching enabled  

## Troubleshooting

### If you still get port conflicts:
1. Kill any existing processes: `pkill -f "python.*app"`
2. Use `python restart_app.py` to start fresh
3. Check that no other apps are using port 5014

### If you need development mode temporarily:
```bash
export DEVELOPMENT_MODE=true
export DEBUG=true
python app.py
```

### To check current port usage:
```bash
lsof -i :5014
```

## Port History
- **Before**: Multiple ports (5001, 5002, 5014) with auto-restarting
- **After**: Fixed port 5014 with no auto-restarting

The app will now start consistently on port 5014 without changing ports or restarting automatically.
