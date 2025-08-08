# Quick Start Guide

## Running the Label Maker App

### Method 1: Using the Start Script (Recommended)
```bash
python start_app.py
```

### Method 2: Direct Launch with Environment Variable
```bash
DISABLE_STARTUP_FILE_LOADING=true python app.py
```

### Method 3: Regular Launch (May hang on startup)
```bash
python app.py
```

## Accessing the App

Once started, open your web browser and go to:
**http://localhost:5001**

## Common Issues

### App Hangs on Startup
- **Problem**: The app tries to load default files on startup which can cause hanging
- **Solution**: Use Method 1 or 2 above to disable startup file loading

### Port Already in Use
- **Problem**: Port 5001 is already being used by another process
- **Solution**: Either stop the other process or change the port by setting `FLASK_PORT` environment variable:
  ```bash
  FLASK_PORT=5002 python start_app.py
  ```

### Import Errors
- **Problem**: Missing dependencies
- **Solution**: Make sure you're in the virtual environment:
  ```bash
  source .venv/bin/activate  # On macOS/Linux
  # or
  .venv\Scripts\activate     # On Windows
  ```

## First Time Setup

1. Start the app using Method 1 above
2. Upload an Excel file using the web interface
3. Generate labels using the available templates

## Stopping the App

Press `Ctrl+C` in the terminal to stop the server. 