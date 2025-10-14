# 🚨 DEPLOY CBD LINEAGE FIX NOW

## The Problem
- CBD Blend products are showing "HYBRID/INDICA" instead of "CBD" in lineage
- The fix is ready in the code but not deployed to PythonAnywhere

## 🚀 QUICK DEPLOYMENT

### Method 1: SSH (Fastest)
```bash
ssh adamcordova@ssh.pythonanywhere.com
cd ~/AGTDesigner
git pull origin main
```

### Method 2: PythonAnywhere Console
1. Go to https://www.pythonanywhere.com/
2. Click "Consoles" → "Bash"
3. Run:
```bash
cd ~/AGTDesigner
git pull origin main
```

## 🔄 RELOAD WEB APP
**CRITICAL: You MUST reload the web app after pulling the code**

1. Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/
2. Click **"Reload"** for www.agtpricetags.com
3. Wait 30 seconds

## 🎯 TEST THE FIX
1. Visit: https://www.agtpricetags.com
2. Upload your Excel file
3. Generate labels
4. Check if "CBD Huckleberry Web" shows "CBD" instead of "HYBRID/INDICA"

## ✅ Expected Result
After deployment and reload:
- ✅ CBD Blend products will show "CBD" lineage
- ✅ Other products remain unchanged
- ✅ No more missing CBD lineage

## 🚨 If Still Not Working
1. **Clear browser cache** (Ctrl+F5 or Cmd+Shift+R)
2. **Try incognito mode**
3. **Check logs**: `tail -f /var/log/www.agtpricetags.com.error.log`

**DEPLOY NOW TO SEE CBD LINEAGE!** 🌿
