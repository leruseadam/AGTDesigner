# Concurrent Users Guide

## Can 7 Users Use the App Simultaneously?

**✅ YES** - 7 users can use the app simultaneously, but with some considerations.

## Current Configuration

### **Local Development:**
- ✅ **Supported concurrent users**: 7-10
- ✅ **Database connections**: 10 max
- ✅ **Threading**: Enabled
- ✅ **Session storage**: 1000 sessions max
- ✅ **File uploads**: 50MB max

### **PythonAnywhere:**
- ✅ **Supported concurrent users**: 5-7 (limited by platform)
- ✅ **Database connections**: 5 max
- ✅ **Threading**: Enabled
- ✅ **Session storage**: 1000 sessions max
- ✅ **File uploads**: 10MB max

## Performance Optimizations Applied

### **1. Database Optimizations**
- **Connection pooling**: 10 connections (5 on PythonAnywhere)
- **Batch processing**: Smaller batches (25) for better concurrency
- **Write locking**: Thread-safe database operations
- **Connection timeouts**: 30 second timeout

### **2. Flask Server Optimizations**
- **Threading enabled**: `threaded=True`
- **Session management**: Filesystem-based sessions
- **Request handling**: Concurrent request processing
- **Memory management**: Optimized for multiple users

### **3. Session Management**
- **Persistent sessions**: Survive browser refreshes
- **Session cleanup**: Automatic cleanup of old sessions
- **Session security**: Signed session cookies
- **Session limits**: 1000 concurrent sessions

## Limitations and Considerations

### **Current Limitations:**
1. **Default Flask Server**: Not production-grade for high load
2. **Single Process**: PythonAnywhere limitation
3. **Memory Usage**: Each user consumes memory
4. **Database Locks**: Heavy operations can cause delays

### **Potential Issues with 7+ Users:**
1. **Database Contention**: Multiple users accessing same data
2. **Memory Pressure**: High memory usage with many users
3. **CPU Usage**: Processing-intensive operations
4. **File I/O**: Concurrent file operations

## Recommendations

### **For 7 Concurrent Users:**

#### **Option 1: Current Setup (Recommended for testing)**
- ✅ **Works well** for 7 users
- ✅ **No additional setup** required
- ⚠️ **Monitor performance** closely

#### **Option 2: Production Setup (Recommended for production)**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -c gunicorn_config.py app:app
```

#### **Option 3: Load Balancing (For 10+ users)**
- Use Nginx as reverse proxy
- Multiple Gunicorn workers
- Database connection pooling

## Monitoring Concurrent Users

### **Performance Metrics to Watch:**
- **Response time**: Should be < 5 seconds
- **CPU usage**: Should be < 80%
- **Memory usage**: Monitor for memory leaks
- **Database connections**: Should not exceed limits
- **Error rate**: Should be < 1%

### **Warning Signs:**
- ⚠️ **Slow response times** (> 10 seconds)
- ⚠️ **High CPU usage** (> 90%)
- ⚠️ **Database locks** (frequent "database is locked" errors)
- ⚠️ **Memory errors** (out of memory)

## Testing Concurrent Users

### **Load Testing Script:**
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test with 7 concurrent users
ab -n 100 -c 7 http://your-domain.com/

# Test file uploads
ab -n 20 -c 7 -T 'multipart/form-data' -p test_file.txt http://your-domain.com/upload
```

### **Manual Testing:**
1. **Open 7 browser tabs/windows**
2. **Access the app simultaneously**
3. **Perform different operations** (upload, generate labels)
4. **Monitor for errors** or slowdowns

## Troubleshooting

### **Common Issues:**

#### **"Database is locked" errors:**
- **Cause**: Too many concurrent database operations
- **Solution**: Reduce concurrent users or optimize database queries

#### **Slow response times:**
- **Cause**: High CPU/memory usage
- **Solution**: Monitor system resources, consider upgrading

#### **Session errors:**
- **Cause**: Session storage issues
- **Solution**: Check session directory permissions

#### **Memory errors:**
- **Cause**: Memory leaks or high usage
- **Solution**: Restart application, monitor memory usage

## Best Practices

### **For Optimal Performance:**
1. **Monitor system resources** regularly
2. **Implement request queuing** for heavy operations
3. **Use caching** for frequently accessed data
4. **Optimize database queries** for concurrent access
5. **Implement rate limiting** for API endpoints

### **For Production Deployment:**
1. **Use Gunicorn** instead of Flask development server
2. **Implement proper logging** and monitoring
3. **Use a reverse proxy** (Nginx) for better performance
4. **Implement health checks** and auto-restart
5. **Use a production database** (PostgreSQL) for better concurrency

## Conclusion

**✅ YES, 7 users can use the app simultaneously** with the current configuration. The system has been optimized for concurrent users with:

- **Threading enabled**
- **Connection pooling**
- **Session management**
- **Optimized database operations**

For production use with 7+ concurrent users, consider using **Gunicorn** for better performance and reliability.
