# 🚀 Development Setup with Auto-Reloading

No more manual restarts! Your Label Maker app now automatically reloads when you make changes to Python files.

## 🎯 Quick Start

### Option 1: Use the shell script (Recommended)
```bash
./start_dev.sh
```

### Option 2: Use the Python script directly
```bash
python run_dev.py
```

### Option 3: Use the original method (still works)
```bash
python app.py
```

## 🔧 What's New

- **Auto-reloading**: Changes to Python files automatically restart the server
- **Development mode**: Debug mode enabled with better error messages
- **Template auto-reload**: HTML templates reload automatically
- **Static file caching disabled**: CSS/JS changes are immediately visible

## 📁 New Files Created

- `config.py` - Development configuration
- `config_production.py` - Production configuration  
- `run_dev.py` - Development startup script
- `start_dev.sh` - Shell script for easy startup
- `DEVELOPMENT_SETUP.md` - This file

## 🌐 Access Your App

Once started, your app will be available at:
- **Local**: http://127.0.0.1:5002
- **Network**: http://your-ip:5002

## ⚙️ Configuration

### Development Mode (Default)
- Auto-reloading enabled
- Debug mode on
- Template auto-reload on
- Static file caching disabled

### Production Mode
To switch to production mode, either:
1. Use `config_production.py` instead of `config.py`
2. Set environment variable: `export DEVELOPMENT_MODE=false`

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## 🔄 How Auto-Reloading Works

1. Flask's built-in reloader watches your Python files
2. When you save changes, it detects file modifications
3. Automatically restarts the server with your changes
4. Your browser will show the updated version

## 🚨 Troubleshooting

### Auto-reload not working?
- Make sure you're using `run_dev.py` or `start_dev.sh`
- Check that `DEVELOPMENT_MODE = True` in `config.py`
- Verify the server shows "Development mode with template auto-reload enabled"

### Port already in use?
- Change the port in `app.py` line 662
- Or kill the existing process: `lsof -ti:5002 | xargs kill -9`

### Virtual environment issues?
- Activate manually: `source venv/bin/activate`
- Or use the shell script which handles this automatically

## 🎉 Enjoy Development!

No more manual restarts - just save your files and see changes immediately!
