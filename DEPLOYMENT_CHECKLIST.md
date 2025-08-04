# PythonAnywhere Deployment Checklist

## ✅ **Completed Optimizations**

### Security Measures
- [x] **File upload validation** - Only .xlsx files, 20MB limit
- [x] **Filename sanitization** - Prevents path traversal attacks
- [x] **CORS restrictions** - Limited to specific origins
- [x] **Session security** - 1-hour lifetime, proper isolation
- [x] **Error handling** - No sensitive information exposed in production
- [x] **Subprocess security** - Shell=False, timeouts, proper error handling

### Performance Optimizations
- [x] **File size limits** - 20MB max upload size
- [x] **Column optimization** - Unused columns dropped early
- [x] **Memory management** - Garbage collection and efficient data structures
- [x] **Background processing** - Non-blocking file processing
- [x] **Session isolation** - Each user gets isolated data

### Resource Management
- [x] **Auto-cleanup system** - Removes old files automatically
- [x] **Rate limiting** - 30 requests per minute per IP
- [x] **Health monitoring** - System status endpoint
- [x] **File cleanup policies** - Age-based and count-based cleanup

## 🚀 **Deployment Steps**

### 1. **Update Configuration**
```python
# In app.py, update CORS origins to your actual domain:
allowed_origins = [
    'https://yourdomain.com',  # Replace with your actual domain
    'https://www.yourdomain.com',
    'http://localhost:9090',  # For local development
    'http://127.0.0.1:9090'
]
```

### 2. **PythonAnywhere Setup**
- [ ] Upload your code to PythonAnywhere
- [ ] Install required dependencies:
  ```bash
  pip install --user flask flask-cors pandas openpyxl python-docx docxtpl psutil
  ```
- [ ] Configure your web app to use the correct Python version
- [ ] Set up your domain or subdomain

### 3. **Environment Configuration**
- [ ] Set `DEVELOPMENT_MODE = False` in your config
- [ ] Ensure `DEBUG = False` in production
- [ ] Configure proper logging levels

### 4. **File Permissions**
- [ ] Ensure uploads/, output/, cache/, and logs/ directories exist
- [ ] Set proper file permissions (755 for directories, 644 for files)

### 5. **Database Setup** (if using)
- [ ] Initialize any required databases
- [ ] Set up proper database permissions

## 📊 **Monitoring & Maintenance**

### Daily Tasks
- [ ] Check PythonAnywhere dashboard for CPU usage
- [ ] Monitor disk space usage
- [ ] Review application logs for errors
- [ ] Check health endpoint: `/api/health`

### Weekly Tasks
- [ ] Review and clean up old files manually if needed
- [ ] Check for dependency updates
- [ ] Review user feedback and performance metrics
- [ ] Backup important data

### Monthly Tasks
- [ ] Update dependencies
- [ ] Review security advisories
- [ ] Analyze usage patterns
- [ ] Optimize based on performance data

## 🔧 **Troubleshooting**

### Common Issues

**High CPU Usage:**
- Check `/api/health` endpoint
- Review background processing logs
- Consider reducing concurrent users

**Disk Space Issues:**
- Trigger manual cleanup: `POST /api/cleanup`
- Check cleanup status: `GET /api/cleanup-status`
- Review file storage policies

**Rate Limiting:**
- Users hitting rate limits will get 429 errors
- Adjust `RATE_LIMIT_MAX_REQUESTS` if needed
- Monitor usage patterns

**Memory Issues:**
- Check health endpoint for memory usage
- Review large file processing
- Consider optimizing data structures

## 📈 **Performance Expectations**

### Your PythonAnywhere Plan
- **Concurrent Users (Light):** 20-50 users browsing/filtering
- **Concurrent Users (Heavy):** 5-10 users uploading/processing
- **Daily Capacity:** 150,000 hits/day
- **Storage:** 5GB total (managed by auto-cleanup)

### Monitoring Thresholds
- **Disk Usage:** >80% triggers warning
- **Memory Usage:** >80% triggers warning
- **File Storage:** >4GB triggers warning
- **Rate Limiting:** 30 requests/minute per IP

## 🛡️ **Security Checklist**

- [x] File upload validation
- [x] Input sanitization
- [x] Session security
- [x] CORS restrictions
- [x] Error handling
- [x] Rate limiting
- [ ] HTTPS configuration
- [ ] Regular security updates
- [ ] Access logging
- [ ] Backup security

## 📞 **Support & Maintenance**

### Emergency Contacts
- PythonAnywhere Support: Available through dashboard
- Application Logs: Check `/logs/` directory
- Health Status: `/api/health` endpoint

### Useful Endpoints
- **Health Check:** `GET /api/health`
- **Cleanup Status:** `GET /api/cleanup-status`
- **Manual Cleanup:** `POST /api/cleanup`
- **System Status:** `GET /api/status`

---

**Your app is now optimized for multi-user deployment on PythonAnywhere!** 🎉 