# PC Performance Troubleshooting Guide

## 🎯 Quick Diagnosis

Your app already has comprehensive PC performance optimizations installed. If you're still experiencing slowness, follow this guide to diagnose and fix the issue.

## 📊 Step 1: Run Diagnostics

### On the PC that's experiencing slowness:

1. Open the web app in Chrome or Edge
2. Press `F12` to open DevTools
3. Go to the **Console** tab
4. Type this command and press Enter:
   ```javascript
   window.runPCDiagnostics()
   ```

5. **Scroll through the page** for 10 seconds during the test
6. Review the diagnostic report

### What to Look For:

✅ **EXCELLENT (55+ FPS)**: No issues  
⚡ **GOOD (40-55 FPS)**: Minor optimizations may help  
⚠️ **FAIR (25-40 FPS)**: Performance needs improvement  
❌ **POOR (<25 FPS)**: Significant issues

## 🔍 Step 2: Check What's Loaded

The diagnostic tool will show:

```
⚙️ Checking Loaded Optimizations:
  PC Performance Boost: ✅ Loaded / ❌ Missing
  Windows Optimizer: ✅ Loaded / ❌ Missing
  Windows CSS: ✅ Loaded / ❌ Missing
  Scroll Behavior: ✅ Auto (fast) / ⚠️ Smooth (slow)
```

### If ANY show ❌ Missing:

The optimization scripts aren't loading. Possible causes:
- Browser cache is stale → Clear cache (Ctrl+Shift+Delete)
- Ad blocker is blocking scripts → Temporarily disable
- Corporate firewall blocking scripts → Check network console

## 🚀 Step 3: Compare Mac vs PC

### On Mac (Safari):
Run the same diagnostic:
```javascript
window.runPCDiagnostics()
```

Compare the FPS values:
- **Mac FPS** should be 55-60 fps
- **PC FPS** should also be 55-60 fps

If PC is significantly lower, continue to Step 4.

## 🔧 Step 4: Common Fixes

### Fix 1: Hard Refresh
```
1. Press Ctrl+Shift+R (Chrome/Edge)
2. Or Ctrl+F5 (Firefox)
3. This forces reload of all scripts/CSS
```

### Fix 2: Clear Browser Cache
```
1. Press Ctrl+Shift+Delete
2. Select "Cached images and files"
3. Time range: "All time"
4. Click "Clear data"
5. Reload the page
```

### Fix 3: Enable Hardware Acceleration
**Chrome/Edge:**
1. Go to `chrome://settings/system`
2. Enable "Use hardware acceleration when available"
3. Restart browser

**Firefox:**
1. Go to `about:preferences#general`
2. Scroll to "Performance"
3. Uncheck "Use recommended performance settings"
4. Check "Use hardware acceleration when available"
5. Restart browser

### Fix 4: Disable Browser Extensions
```
1. Open browser in Incognito/Private mode
2. Test if performance improves
3. If yes, disable extensions one by one to find culprit
```

### Fix 5: Update Graphics Drivers
```
1. Press Win+X → Device Manager
2. Expand "Display adapters"
3. Right-click your graphics card
4. Select "Update driver"
5. Restart computer
```

## 📈 Step 5: Monitor Performance Live

### Continuous FPS Monitoring:
```javascript
window.monitorFPS()
```

This will show live FPS updates in console:
```
✅ FPS: 60
✅ FPS: 58
⚠️ FPS: 28  ← Performance dip detected
```

To stop monitoring:
```javascript
window.stopFPSMonitoring()
```

### Use Chrome Performance Profiler:
1. Open DevTools (F12)
2. Go to "Performance" tab
3. Click record button (●)
4. Scroll through the app for 5 seconds
5. Stop recording
6. Look for:
   - Red bars (long tasks) → Should be minimal
   - FPS graph → Should stay above 30fps
   - Yellow bars (scripting) → Should be evenly distributed

## 🐛 Step 6: Identify Specific Bottlenecks

### Test Individual Actions:

**Test 1: Scrolling Tag Lists**
```
1. Monitor FPS: window.monitorFPS()
2. Scroll through Available Tags list
3. FPS should stay 55-60
4. If drops: Issue is with tag rendering
```

**Test 2: Searching/Filtering**
```
1. Monitor FPS
2. Type in search box
3. Should have <50ms input lag
4. If laggy: Issue is with search debouncing
```

**Test 3: Generating Labels**
```
1. Select 10 tags
2. Click "Generate Labels"
3. Should complete in <10 seconds
4. If slower: Issue is backend, not frontend
```

**Test 4: Opening Modals**
```
1. Monitor FPS
2. Open settings modal
3. Should animate smoothly
4. If choppy: Issue is with modal animations
```

## 💡 Step 7: Specific Problem Solutions

### Problem: Scrolling is choppy
**Solution:**
```javascript
// Add this to console to force native scrolling
document.documentElement.style.scrollBehavior = 'auto';
document.querySelectorAll('*').forEach(el => {
    el.style.scrollBehavior = 'auto';
    el.style.transform = 'none';
    el.style.willChange = 'auto';
});
```

### Problem: Tag list is slow with 1000+ items
**Solution:** Virtual scrolling should activate automatically. Verify:
```javascript
// Check if virtual scrolling is active
console.log(window.pcBoost?.virtualScrollingActive);
// Should be true for lists with 50+ items
```

### Problem: Animations are laggy
**Solution:**
```javascript
// Disable all animations temporarily
const style = document.createElement('style');
style.textContent = `
    * {
        transition: none !important;
        animation: none !important;
    }
`;
document.head.appendChild(style);
```

### Problem: High CPU usage
**Check what's causing it:**
```javascript
// Run this and look for warnings
performance.measure('app-performance');
```

## 📋 Step 8: Report Findings

If none of the above fixes work, gather this information:

### System Info:
```javascript
// Run in console
console.log({
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    cores: navigator.hardwareConcurrency,
    memory: navigator.deviceMemory,
    connection: navigator.connection?.effectiveType
});
```

### Performance Metrics:
```javascript
// After running diagnostics
window.pcDiagnostics.metrics
```

### Browser Console Errors:
1. Open Console (F12)
2. Look for red error messages
3. Screenshot any errors

### Network Issues:
1. Go to Network tab in DevTools
2. Reload page
3. Look for:
   - Failed requests (red)
   - Slow requests (>1 second)
   - Large files (>500KB)

## 🎯 Most Common Causes & Quick Fixes

### Issue: "Optimizations not loading"
**Fix:** Hard refresh (Ctrl+Shift+R)

### Issue: "Low FPS only on one PC"
**Fix:** Update graphics drivers

### Issue: "Slow in Chrome but fast in Edge"
**Fix:** Disable Chrome extensions

### Issue: "Slow on all PCs but fast on Mac"
**Fix:** This shouldn't happen with optimizations. Run diagnostics to identify specific bottleneck.

### Issue: "Was fast yesterday, slow today"
**Fix:** Clear browser cache

## 🔬 Advanced: Add Temporary Performance Monitor

Add this to your URL to auto-run diagnostics:
```
https://www.agtpricetags.com?diagnose=true
```

This will automatically run diagnostics after 2 seconds and show results in console.

## 📞 Still Having Issues?

If you've tried all the above and PC is still slower than Mac:

1. **Compare specific metrics:**
   - Mac FPS: [fill in]
   - PC FPS: [fill in]
   - Mac load time: [fill in]
   - PC load time: [fill in]

2. **Check specific action:**
   - What exactly is slow? (scrolling, generating, searching, etc.)
   - How much slower? (2x, 5x, 10x?)
   - Does it happen immediately or after using the app for a while?

3. **Verify hardware:**
   - PC specs (CPU, RAM, Graphics card)
   - Mac specs for comparison
   - Are they comparable hardware?

## ✅ Expected Performance

With optimizations active:

| Action | Mac Safari | PC Chrome/Edge | Status |
|--------|-----------|----------------|---------|
| Page Load | 1-2 sec | 1-2 sec | ✅ Equal |
| Scrolling | 60 fps | 55-60 fps | ✅ Equal |
| Tag Search | <50ms | <50ms | ✅ Equal |
| Label Gen (10 tags) | 3-5 sec | 3-5 sec | ✅ Equal |
| Label Gen (50 tags) | 8-12 sec | 8-12 sec | ✅ Equal |

If PC performance is significantly worse than these benchmarks, the diagnostics will help identify why.

---

**Last Updated**: October 21, 2025  
**Version**: 1.0

