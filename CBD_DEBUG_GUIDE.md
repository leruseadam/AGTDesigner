# 🔍 CBD LINEAGE DEBUGGING GUIDE

## The Issue
"CBD Huckleberry Web" is still showing "HYBRID" instead of "CBD" even after deployment.

## 🚀 Deploy Debug Version

**Pull the latest code with debug logging:**
```bash
ssh adamcordova@ssh.pythonanywhere.com
cd ~/AGTDesigner
git pull origin main
```

**Reload web app:**
1. Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/
2. Click "Reload" for www.agtpricetags.com

## 🔍 Check Debug Logs

**View the logs to see what's happening:**
```bash
tail -f /var/log/www.agtpricetags.com.error.log
```

**Look for these debug messages:**
- `CBD DETECTION DEBUG (classic): product_name='CBD Huckleberry Web', product_type='Flower', product_strain='...', is_cbd_product=True/False`
- `CBD DETECTION DEBUG (non-classic): product_name='CBD Huckleberry Web', product_type='Flower', product_strain='...', is_cbd_product=True/False`

## 🎯 What to Look For

**If `is_cbd_product=True`:**
- The detection is working
- The issue might be elsewhere in the code

**If `is_cbd_product=False`:**
- The detection logic needs adjustment
- Check what values are being passed for product_name, product_type, product_strain

## 📋 Expected Debug Output

For "CBD Huckleberry Web", you should see:
```
CBD DETECTION DEBUG: product_name='CBD Huckleberry Web', product_type='Flower', product_strain='...', is_cbd_product=True
CBD PRODUCT FIX: Overriding lineage to 'CBD' for product 'CBD Huckleberry Web'
```

## 🚨 If Still Not Working

**Check these possibilities:**
1. **Product name field**: Might be stored differently in Excel
2. **Case sensitivity**: Product name might be "cbd huckleberry web" (lowercase)
3. **Field mapping**: Product name might be in a different column
4. **Template type**: Might be using a different code path

**Share the debug log output** and I can fix the detection logic accordingly.

## ⚡ Quick Test

**Generate labels and check logs immediately** - the debug messages will show exactly what's happening with CBD detection.
