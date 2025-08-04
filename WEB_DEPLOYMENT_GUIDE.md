# Web Deployment Guide for Label Maker

## 🌐 PythonAnywhere Deployment

### Quick Setup (5 minutes)

1. **Log into PythonAnywhere**
   - Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
   - Log into your account

2. **Clone Repository**
   ```bash
   git clone https://github.com/leruseadam/AGTDesigner.git
   cd AGTDesigner
   git checkout restored-working-version
   ```

3. **Create Virtual Environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements_pythonanywhere.txt
   pip install flask-caching python-dotenv gunicorn
   ```

4. **Configure Web App**
   - Go to **Web** tab in PythonAnywhere
   - Click **Add a new web app**
   - Choose **Manual configuration**
   - Python version: **3.11**
   - Source code: `/home/yourusername/AGTDesigner`
   - Working directory: `/home/yourusername/AGTDesigner`
   - WSGI configuration file: `/home/yourusername/AGTDesigner/wsgi.py`

5. **Set Environment Variables**
   - In Web tab, go to **Environment variables**
   - Add: `FLASK_ENV=production`
   - Add: `FLASK_DEBUG=False`

6. **Reload Web App**
   - Click **"Reload"** button in Web tab

## 📁 File Structure

```
AGTDesigner/
├── app.py                           # Main application
├── wsgi.py                          # WSGI entry point
├── pythonanywhere_config.py         # Configuration
├── requirements_pythonanywhere.txt   # Dependencies
├── static/                          # CSS, JS, images
├── templates/                       # HTML templates
├── src/                            # Source code
└── product_database.db              # Database
```

## 🔧 Configuration Details

### WSGI Configuration (wsgi.py)
- Entry point for PythonAnywhere
- Imports your Flask app
- Sets up proper Python path

### Environment Variables
- `FLASK_ENV=production` - Production mode
- `FLASK_DEBUG=False` - Disable debug mode
- Database path automatically configured

### Virtual Environment
- Python 3.11
- All dependencies from `requirements_pythonanywhere.txt`
- Additional web-specific packages

## 🚀 Deployment Steps

### Step 1: Prepare Your Project
```bash
# Ensure you're in the right directory
cd /Users/adamcordova/Desktop/labelMaker_backup_20250803_182324

# Test web environment
source venv_web/bin/activate
python -c "from app import create_app; print('✅ Ready for deployment!')"
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Add web deployment configuration"
git push origin restored-working-version
```

### Step 3: Deploy on PythonAnywhere
1. Log into PythonAnywhere
2. Open a **Bash console**
3. Run the deployment commands above
4. Configure the web app
5. Reload and test

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Solution: Install missing dependencies
pip install flask-caching python-dotenv gunicorn
```

**Database Errors**
```bash
# Solution: Check file permissions
chmod 644 product_database.db
```

**Static Files Not Loading**
- Ensure `static/` and `templates/` directories exist
- Check file permissions
- Verify paths in configuration

**Port Issues**
- PythonAnywhere handles ports automatically
- No manual port configuration needed

### Debugging

**Check Logs**
- Go to **Web** tab in PythonAnywhere
- Click **Error log** to see issues

**Test Locally**
```bash
# Test web environment locally
source venv_web/bin/activate
python wsgi.py
```

**Monitor Application**
- Use **Files** tab to browse project
- Use **Console** for debugging
- Check **Web** tab for status

## 📊 Monitoring

### Health Checks
- Application loads without errors
- Database connects successfully
- Static files serve correctly
- Templates render properly

### Performance
- Monitor response times
- Check memory usage
- Review error logs regularly

## 🔄 Updates

### Updating Your Application
1. Make changes locally
2. Test with web environment
3. Push to GitHub
4. Pull on PythonAnywhere
5. Reload web app

### Environment Updates
```bash
# Update dependencies
pip install --upgrade -r requirements_pythonanywhere.txt

# Update virtual environment
source venv/bin/activate
pip install --upgrade pip
```

## ✅ Success Checklist

- [ ] Repository cloned on PythonAnywhere
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] Web app configured in PythonAnywhere
- [ ] WSGI file points to correct app
- [ ] Environment variables set
- [ ] Web app reloaded successfully
- [ ] Application accessible via URL
- [ ] Database loads correctly
- [ ] All features working

## 🎯 Your Web URL

Once deployed, your application will be available at:
```
https://yourusername.pythonanywhere.com
```

## 🚀 Ready to Deploy!

Your Label Maker application is now ready for web deployment on PythonAnywhere. Follow the steps above to get your application live on the web! 