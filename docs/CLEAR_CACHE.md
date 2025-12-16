# 🧹 Clear Cached Versions - Complete Guide

## The Problem

The service worker aggressively caches everything for performance. This is great for speed but means you might see old versions during development.

---

## 🚀 Quick Solutions

### Option 1: Hard Refresh (Simplest)

**Mac:** `Cmd + Shift + R`
**Windows/Linux:** `Ctrl + Shift + F5`

This bypasses the cache for one page load.

---

### Option 2: Clear All Caches (Recommended)

**In Browser Console** (F12):

```javascript
// Clear all caches and reload
(async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(key => caches.delete(key)));
    console.log('✅ All caches cleared:', keys);
    location.reload();
})();
```

---

### Option 3: Unregister Service Worker (Nuclear Option)

**In Browser Console:**

```javascript
// Unregister service worker and clear everything
(async () => {
    // Unregister all service workers
    const registrations = await navigator.serviceWorker.getRegistrations();
    await Promise.all(registrations.map(reg => reg.unregister()));
    
    // Clear all caches
    const keys = await caches.keys();
    await Promise.all(keys.map(key => caches.delete(key)));
    
    console.log('✅ Service workers unregistered');
    console.log('✅ All caches cleared');
    console.log('🔄 Reloading...');
    
    location.reload();
})();
```

---

### Option 4: DevTools Application Tab

1. Open DevTools (`F12`)
2. Go to **Application** tab
3. In sidebar, click **Clear storage**
4. Check all boxes
5. Click **Clear site data**
6. Reload page

---

### Option 5: Enable Development Mode

Edit `static/service-worker.js`:

```javascript
// Line 10: Change false to true
const DEV_MODE = true;  // 🔧 DEVELOPMENT MODE
```

Then:
1. Save file
2. Unregister old service worker (use Option 3 above)
3. Reload page
4. Now NO caching happens (always gets fresh files)

**Remember to set back to `false` for production!**

---

## 🔄 Force New Cache Version

If you want to force all users to get fresh files:

Edit `static/service-worker.js`:

```javascript
// Line 13: Increment version number
const CACHE_VERSION = 'v4';  // Was v3, now v4
```

This will:
- Delete old v3 cache
- Create new v4 cache
- Force fresh downloads

---

## 🎯 Best Practice: Development Workflow

### During Development:

**Method A: Use DEV_MODE**
```javascript
// static/service-worker.js line 10:
const DEV_MODE = true;
```
- No caching, always fresh
- Unregister service worker first
- Remember to set back to false!

**Method B: Use Chrome Incognito**
- Opens without cache
- Service worker won't persist
- Clean slate each time

**Method C: Disable Service Worker in DevTools**
1. DevTools → Application → Service Workers
2. Check "Bypass for network"
3. Keeps DevTools open while testing

### For Production:

```javascript
// static/service-worker.js line 10:
const DEV_MODE = false;
```
- Full caching enabled
- Maximum performance
- Increment CACHE_VERSION when deploying changes

---

## 📋 Checklist: "I Want Fresh Files"

- [ ] Hard refresh: `Cmd + Shift + R`
- [ ] Clear caches (use Option 2 above)
- [ ] Unregister service worker (use Option 3 above)
- [ ] Reload page
- [ ] Check console for "Service Worker registered" (or not if unregistered)
- [ ] Verify changes are visible

---

## 🔍 Verify Cache Status

### Check if service worker is active:

```javascript
navigator.serviceWorker.getRegistrations().then(regs => {
    console.log('Active service workers:', regs.length);
    regs.forEach(reg => console.log('Scope:', reg.scope));
});
```

### Check what's cached:

```javascript
caches.keys().then(keys => {
    console.log('Cache names:', keys);
    keys.forEach(async key => {
        const cache = await caches.open(key);
        const requests = await cache.keys();
        console.log(`${key}: ${requests.length} items`);
    });
});
```

### Check current version:

```javascript
// Service worker tells you in console:
// Look for: "[Service Worker] Installing..." messages
```

---

## ⚡ Quick Commands

Copy and paste these into browser console (`F12`):

### 1. Clear Everything:
```javascript
(async()=>{await Promise.all((await caches.keys()).map(k=>caches.delete(k)));await Promise.all((await navigator.serviceWorker.getRegistrations()).map(r=>r.unregister()));location.reload()})();
```

### 2. Check Cache Status:
```javascript
(async()=>{console.log('Caches:',(await caches.keys()));console.log('SW:',(await navigator.serviceWorker.getRegistrations()).length)})();
```

### 3. Clear Just Caches (Keep SW):
```javascript
(async()=>{await Promise.all((await caches.keys()).map(k=>caches.delete(k)));location.reload()})();
```

---

## 🎓 Understanding Service Worker Caching

### What Gets Cached:

✅ **CSS files** (`/static/css/*.css`)
✅ **JavaScript files** (`/static/js/*.js`)
✅ **Images** (if added to STATIC_ASSETS)
✅ **API responses** (5-minute TTL)
✅ **HTML pages** (session)

### What Doesn't Get Cached:

❌ **POST requests** (mutations)
❌ **PUT/DELETE requests** (updates)
❌ **WebSocket connections**
❌ **Files not in STATIC_ASSETS list**

### Cache Strategy:

- **Static files:** Cache first, network fallback
- **API calls:** Network first, cache fallback
- **HTML:** Network first, cache fallback

---

## 🐛 Troubleshooting

### "I cleared cache but still see old version"

1. Check if service worker is still registered:
   ```javascript
   navigator.serviceWorker.getRegistrations().then(r=>console.log(r.length))
   ```

2. If it shows `1` or more, unregister:
   ```javascript
   (async()=>{await Promise.all((await navigator.serviceWorker.getRegistrations()).map(r=>r.unregister()));console.log('Done')})();
   ```

3. Close ALL tabs with your app
4. Open fresh tab
5. Hard refresh

### "Changes not showing even after clearing"

- Make sure Flask app was restarted
- Check browser isn't using disk cache (DevTools → Network → Disable cache)
- Try Incognito window
- Check the actual file on disk has your changes

### "Service worker won't unregister"

1. Close all tabs with your app
2. Open one fresh tab
3. Run unregister command
4. Wait 5 seconds
5. Close tab
6. Open new tab

---

## 📝 Summary

**Quick fix:** `Cmd + Shift + R` (hard refresh)

**Nuclear option:** Copy into console:
```javascript
(async()=>{await Promise.all((await caches.keys()).map(k=>caches.delete(k)));await Promise.all((await navigator.serviceWorker.getRegistrations()).map(r=>r.unregister()));location.reload()})();
```

**Development mode:** Set `DEV_MODE = true` in `static/service-worker.js`

---

**You should now be able to see fresh versions!** 🎉

