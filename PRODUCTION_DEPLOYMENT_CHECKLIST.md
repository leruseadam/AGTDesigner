# Production Server Database Fix Deployment Checklist

## 🎯 **Objective**
Fix the 500 Internal Server Error on `https://www.agtpricetags.com/api/database-vendor-stats` by deploying the working database and code fixes.

## 📋 **Pre-Deployment Verification**

### ✅ **Local Environment Status**
- [x] Database working locally with 2193 strains and 5791 products
- [x] Database path correctly configured in `uploads/product_database.db`
- [x] Safe schema migration implemented
- [x] `sovereign_lineage` column exists in database
- [x] All code fixes committed and pushed to repository

### 📊 **Current Production Status**
- [ ] Production server returning 500 errors on database endpoints
- [ ] Database integration disabled or corrupted
- [ ] Missing or empty database file

## 🚀 **Deployment Steps**

### **Step 1: Access Production Server**
```bash
# SSH into the production server
ssh username@agtpricetags.com

# Navigate to project directory
cd /path/to/labelmaker/project
```

### **Step 2: Update Code**
```bash
# Pull latest fixes from repository
git pull origin main

# Verify the updated files are present
ls -la src/core/data/product_database.py
ls -la app.py
ls -la config.py
```

### **Step 3: Transfer Working Database**
```bash
# From your local machine, transfer the database
scp uploads/product_database.db username@agtpricetags.com:/path/to/labelmaker/uploads/

# Verify transfer on production server
ls -lh uploads/product_database.db
# Should show ~80MB file size
```

### **Step 4: Restart Application**
```bash
# Option A: If using systemd service
sudo systemctl restart labelmaker

# Option B: If running manually
pkill -f "python app.py"
python app.py

# Option C: If using screen/tmux
# Find the session and restart it
```

### **Step 5: Enable Database Integration**
```bash
# The database integration is disabled by default for performance
# Enable it via API call after restart
curl -X POST "https://www.agtpricetags.com/api/product-db/enable"
```

## ✅ **Post-Deployment Verification**

### **Test Database Endpoints**
```bash
# Test database stats endpoint
curl "https://www.agtpricetags.com/api/database-vendor-stats"

# Test product database status
curl "https://www.agtpricetags.com/api/product-db/status"

# Test strain endpoint
curl "https://www.agtpricetags.com/api/get-all-strains"
```

### **Expected Results**
- ✅ No more 500 errors
- ✅ Database stats returned with actual data
- ✅ Strain list populated with 2193+ strains
- ✅ Product database integration enabled

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **Issue: Still getting 500 errors**
- **Solution**: Check production server logs for specific error messages
- **Command**: `tail -f /path/to/labelmaker/logs/app.log`

#### **Issue: Database file not found**
- **Solution**: Verify database path in production `config.py` and `app.py`
- **Check**: Ensure path points to `uploads/product_database.db`

#### **Issue: Permission denied on database**
- **Solution**: Check file permissions and ownership
- **Command**: `ls -la uploads/product_database.db`

#### **Issue: Database integration still disabled**
- **Solution**: Manually enable via API endpoint
- **Command**: `curl -X POST "https://www.agtpricetags.com/api/product-db/enable"`

## 📞 **Support**

If deployment fails:
1. Check production server logs
2. Verify database file transfer
3. Confirm code updates were applied
4. Test database connectivity manually

## 🎉 **Success Criteria**

The deployment is successful when:
- [ ] `https://www.agtpricetags.com/api/database-vendor-stats` returns data instead of 500 error
- [ ] Database shows 2193+ strains and 5791+ products
- [ ] All database endpoints respond correctly
- [ ] Web interface displays database analytics properly
