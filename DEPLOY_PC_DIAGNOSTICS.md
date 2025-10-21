# Deploy PC Performance Diagnostics to Production

## 🎯 What Was Added

We've added a comprehensive PC performance diagnostic tool to identify why the PC version is slower than Mac.

**New Files:**
- `static/js/pc-performance-diagnostics.js` - Client-side diagnostic tool
- `PC_PERFORMANCE_TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `PC_PERFORMANCE_SOLUTION.md` - Quick reference guide

**Modified Files:**
- `templates/base.html` - Added diagnostic script

## 📤 Deploy to PythonAnywhere

### Step 1: SSH to PythonAnywhere and Pull Changes

```bash
# On PythonAnywhere Bash console:
cd /home/YOUR_USERNAME/your-app-directory
git pull origin main
```

### Step 2: Reload Web App

1. Go to https://www.pythonanywhere.com
2. Click **Web** tab
3. Click **Reload** button for your web app

### Step 3: Verify Deployment

Visit your site and check the console:
```
✅ PC Performance Diagnostics loaded
   Run: window.runPCDiagnostics() to start
```

## 🔍 Run Diagnostics on Affected PC

### On the PC that's experiencing slowness:

1. **Open the site** in Chrome or Edge: https://www.agtpricetags.com

2. **Open Developer Console:**
   - Press `F12` (Windows)
   - Or right-click → Inspect → Console tab

3. **Run the diagnostic tool:**
   ```javascript
   window.runPCDiagnostics()
   ```

4. **During the 10-second test:**
   - Scroll through the page
   - Interact with tag lists
   - Try normal workflows

5. **Review the report** that appears in console

### What to Look For:

```
📋 DIAGNOSTIC REPORT SUMMARY
═══════════════════════════════════════

✅ EXCELLENT: Performance is optimal (55+ FPS)
⚡ GOOD: Performance is acceptable (40-55 FPS)  
⚠️ FAIR: Performance needs improvement (25-40 FPS)
❌ POOR: Significant issues (<25 FPS)
```

## 🔧 Quick Fixes to Try First

### Fix 1: Hard Refresh (Most Common Solution)
```
Ctrl + Shift + R  (Chrome/Edge)
Ctrl + F5         (Firefox)
```

### Fix 2: Clear Browser Cache
```
Ctrl + Shift + Delete
→ Select "Cached images and files"
→ Time range: "All time"
→ Click "Clear data"
```

### Fix 3: Enable Hardware Acceleration

**Chrome/Edge:**
1. Go to `chrome://settings/system`
2. Enable "Use hardware acceleration when available"
3. Restart browser

### Fix 4: Test in Incognito Mode
```
Ctrl + Shift + N
```
If it's faster in Incognito, a browser extension is causing the issue.

## 📊 Compare Mac vs PC

### On Mac (for comparison):
1. Open Safari DevTools: `Cmd + Option + C`
2. Go to Console tab
3. Run: `window.runPCDiagnostics()`
4. Note the FPS values

### Expected Results:
- **Mac Safari:** 55-60 FPS ✅
- **PC Chrome/Edge:** 55-60 FPS ✅ (should be equal!)

If PC is significantly lower (e.g., 20-30 FPS), the diagnostic report will tell you why.

## 🎯 Continuous Monitoring

To watch FPS in real-time while using the app:

```javascript
// Start monitoring
window.monitorFPS()

// Use the app normally, watch console for FPS updates

// Stop monitoring
window.stopFPSMonitoring()
```

## 🐛 Common Issues & Solutions

### Issue: "Optimizations not loading"
**Check in diagnostic output:**
```
⚙️ Checking Loaded Optimizations:
  PC Performance Boost: ❌ Missing
```

**Solution:**
1. Hard refresh (Ctrl+Shift+R)
2. Clear cache
3. Check if ad blocker is interfering

### Issue: "Scroll Behavior is Smooth"
**Check in diagnostic output:**
```
  Scroll Behavior: ⚠️ Smooth (slow)
```

**Solution:** The optimization should fix this automatically. If not:
```javascript
document.documentElement.style.scrollBehavior = 'auto';
```

### Issue: "High scroll event count"
**Check in diagnostic output:**
```
  Scroll Events: 250 ⚠️ Too many
```

**Solution:** Event throttling should be active. If not, there may be JS errors preventing optimization loading.

## 📋 Report Back With:

After running diagnostics on the affected PC, please provide:

1. **FPS Results:**
   - Average FPS: [??]
   - Minimum FPS: [??]
   - Status (Excellent/Good/Fair/Poor): [??]

2. **Optimization Status:**
   - PC Performance Boost: ✅/❌
   - Windows Optimizer: ✅/❌
   - Windows CSS: ✅/❌

3. **Platform Info:**
   - Browser: Chrome/Edge/Firefox/Other
   - Version: [??]
   - Windows Version: [??]

4. **Specific Slowness:**
   - What exactly is slow? (scrolling, searching, generating, page load, etc.)
   - How much slower than Mac? (a little/noticeably/very slow)

## 🚨 If Diagnostics Show Problems

The diagnostic tool will automatically provide specific recommendations based on what it finds.

For detailed troubleshooting, see: `PC_PERFORMANCE_TROUBLESHOOTING.md`

---

## ⚡ Auto-Run Diagnostics

You can also add `?diagnose=true` to the URL to automatically run diagnostics:

```
https://www.agtpricetags.com?diagnose=true
```

This will auto-run the diagnostic test after 2 seconds of page load.

---

**Last Updated:** October 21, 2025  
**Status:** Ready to deploy and test

