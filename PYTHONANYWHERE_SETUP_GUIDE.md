# PythonAnywhere Deployment Guide

This guide will help you deploy your LabelMaker application to PythonAnywhere with zero differences from your local version.

## 🚀 Quick Deployment Steps

### 1. Create Deployment Package
```bash
python deploy_to_pythonanywhere.py
```

This will create:
- `pythonanywhere_deployment/` directory with all files
- `labelmaker_pythonanywhere.zip` for easy upload

### 2. Upload to PythonAnywhere

#### Option A: Using the zip file
1. Go to your PythonAnywhere dashboard
2. Open the Files tab
3. Upload `labelmaker_pythonanywhere.zip`
4. Extract it in your home directory

#### Option B: Using git (recommended)
1. Go to your PythonAnywhere console
2. Run:
```bash
git clone https://github.com/leruseadam/AGTDesigner.git
cd AGTDesigner
```

### 3. Install Dependencies
```bash
pip3.10 install --user -r requirements.txt
```

### 4. Set Up Web App
1. Go to Web tab in PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10
5. Set source code path to your app directory
6. Set WSGI file to: `/home/yourusername/AGTDesigner/app.py`
7. Click "Reload" to start the app

## 🔧 Detailed Setup Instructions

### Database Setup
The SQLite database (`product_database.db`) is included and ready to use. No additional setup required.

### Static Files
Static files are in the `static/` directory and will be served automatically.

### Sessions
The `sessions/` directory will be created automatically when the app runs.

### Environment Variables
No environment variables are required for basic functionality.

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure you're using Python 3.10
   - Check that all dependencies are installed
   - Verify the source code path is correct

2. **Database Errors**
   - Ensure `product_database.db` is in the correct location
   - Check file permissions

3. **Static Files Not Loading**
   - Verify static files are in the `static/` directory
   - Check the web app configuration

4. **App Not Starting**
   - Check the error logs in the Web tab
   - Verify all required files are present

### File Structure Verification
Your deployed app should have this structure:
```
/home/yourusername/AGTDesigner/
├── app.py
├── requirements.txt
├── product_database.db
├── src/
│   └── core/
│       └── data/
│           └── product_database.py
├── static/
│   └── js/
│       └── main.js
├── templates/
│   └── index.html
└── [Excel database files]
```

## ✅ Verification Checklist

- [ ] All files uploaded successfully
- [ ] Dependencies installed without errors
- [ ] Web app configured correctly
- [ ] App starts without errors
- [ ] Database loads correctly
- [ ] Static files load properly
- [ ] Templates render correctly

## 🆘 Support

If you encounter issues:
1. Check the error logs in PythonAnywhere
2. Verify file permissions
3. Ensure all dependencies are installed
4. Check that the database file is present and accessible

## 📝 Notes

- The deployment package excludes temporary files and sessions
- The database is included and contains all your product data
- No additional configuration is required
- The app will work exactly as it does locally