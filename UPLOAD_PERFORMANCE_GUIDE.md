# File Upload Performance Optimization Guide

## 🚀 Quick Performance Fixes

### 1. **Use the Simple Upload Endpoint**
If uploads are slow, try using the `/upload-simple` endpoint instead of `/upload`:
- Faster processing
- Less memory usage
- Immediate response

### 2. **Check File Size**
- **Small files (< 5MB)**: Should upload in 1-3 seconds
- **Medium files (5-25MB)**: Should upload in 3-10 seconds
- **Large files (25-50MB)**: Should upload in 10-30 seconds

### 3. **Optimize Excel Files**
- Remove unnecessary columns
- Remove empty rows
- Use .xlsx format (not .xls)
- Avoid complex formulas

## 🔧 Advanced Optimizations

### 1. **Background Processing**
The app uses background processing for large files:
- File uploads immediately
- Processing continues in background
- Check status with `/status` endpoint

### 2. **Memory Management**
- Automatic garbage collection
- Chunked reading for large files
- Memory usage monitoring

### 3. **Cache Optimization**
- Smart caching system
- Minimal cache clearing
- File result caching

## 📊 Performance Monitoring

### Check Upload Status
```bash
curl http://your-domain/status
```

### Monitor Memory Usage
```bash
# Check if psutil is available
python -c "import psutil; print('Memory monitoring available')"
```

### Test Performance
```bash
python test_upload_performance.py
```

## 🚨 Common Issues and Solutions

### Issue: Upload Takes Too Long
**Solutions:**
1. Use `/upload-simple` endpoint
2. Check file size and optimize Excel file
3. Ensure background processing is enabled
4. Check server resources

### Issue: Memory Errors
**Solutions:**
1. Reduce file size
2. Remove unnecessary columns
3. Split large files
4. Enable chunked reading

### Issue: Timeout Errors
**Solutions:**
1. Increase timeout settings
2. Use smaller files
3. Check network connection
4. Enable background processing

## 🎯 Performance Targets

| File Size | Target Upload Time | Target Processing Time |
|-----------|-------------------|----------------------|
| < 1MB     | < 1 second       | < 2 seconds         |
| 1-5MB     | < 2 seconds      | < 5 seconds         |
| 5-25MB    | < 3 seconds      | < 15 seconds        |
| 25-50MB   | < 5 seconds      | < 30 seconds        |

## 🔍 Troubleshooting

### Run Performance Tests
```bash
python test_upload_performance.py
```

### Check Logs
```bash
tail -f logs/app.log | grep UPLOAD
```

### Monitor Resources
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top
```

## 📞 Support

If uploads are still slow after trying these optimizations:
1. Check the performance test results
2. Review the logs for errors
3. Consider file size and complexity
4. Contact support with specific performance data
