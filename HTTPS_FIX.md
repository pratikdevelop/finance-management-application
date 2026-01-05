# Fix: HTTPS to HTTP Redirect Issue

## Problem
Your Angular app is using HTTP in the code, but requests are being converted to HTTPS automatically.

## ✅ Your Configuration is Correct!

I've verified:
- ✅ `environment.ts` uses `http://127.0.0.1:8000/`
- ✅ `package.json` has `--ssl false` in start script
- ✅ Angular is configured for HTTP

## 🔍 Root Causes & Solutions

### Solution 1: Clear Browser Cache & HSTS Settings

**Chrome/Edge:**
1. Open browser
2. Go to: `chrome://net-internals/#hsts`
3. In "Delete domain security policies" section
4. Enter: `localhost`
5. Click "Delete"
6. Also try: `127.0.0.1`
7. Close and restart browser

**Firefox:**
1. Close Firefox completely
2. Delete file: `SiteSecurityServiceState.txt` from profile folder
3. Restart Firefox

**Or simply:**
- Open browser in **Incognito/Private mode**
- This bypasses cached HSTS settings

---

### Solution 2: Use Different Port or Host

Instead of `localhost`, use `127.0.0.1` directly:

**Update your services to use:**
```typescript
// Instead of localhost
apiUrl = 'http://127.0.0.1:8000/api/';
```

**Or change Angular port:**
```bash
ng serve --port 4201 --ssl false
```

---

### Solution 3: Disable Browser HTTPS Enforcement

**Chrome:**
1. Right-click Chrome shortcut
2. Add flag: `--disable-features=ForceWebContentsDarkMode`
3. Or use: `--ignore-certificate-errors`

**For development only!**

---

### Solution 4: Check for Service Worker

If you have a service worker, it might be caching HTTPS:

```bash
# In browser console
navigator.serviceWorker.getRegistrations().then(function(registrations) {
  for(let registration of registrations) {
    registration.unregister();
  }
});
```

---

### Solution 5: Restart Angular with Clean Cache

```bash
# Stop Angular server (Ctrl+C)

# Clear Angular cache
rm -rf .angular

# Clear node modules cache (if needed)
npm cache clean --force

# Restart
npm start
```

---

### Solution 6: Add Proxy Configuration (Recommended)

Create `proxy.conf.json` in frontend root:

```json
{
  "/api": {
    "target": "http://127.0.0.1:8000",
    "secure": false,
    "changeOrigin": true,
    "logLevel": "debug"
  }
}
```

Update `package.json`:
```json
"start": "ng serve --proxy-config proxy.conf.json --ssl false"
```

Then in your services, use relative URLs:
```typescript
apiUrl = '/api/';  // No need for full URL
```

---

### Solution 7: Check Django CORS Settings

Ensure Django allows HTTP requests:

In `settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True  # Already set
SECURE_SSL_REDIRECT = False    # Should be False for development
```

---

## 🧪 Quick Test

1. **Stop Angular server** (Ctrl+C)
2. **Clear browser cache** (Ctrl+Shift+Delete)
3. **Open Incognito window**
4. **Restart Angular:**
   ```bash
   npm start
   ```
5. **Access:** `http://localhost:4200`

---

## 🎯 Recommended Solution

**Best approach for development:**

1. **Use proxy configuration** (Solution 6)
2. **Access via Incognito** first time
3. **Clear HSTS settings** for localhost

This will ensure:
- No HTTPS redirects
- Proper CORS handling
- Clean development environment

---

## 📝 Verify Your Setup

**Check these URLs in browser:**

1. Frontend: `http://localhost:4200`
2. Backend API: `http://127.0.0.1:8000/api/`
3. Admin: `http://127.0.0.1:8000/admin/`

**All should use HTTP (no 's')**

---

## 🔒 For Production

When deploying to production:
- Use HTTPS everywhere
- Get SSL certificate
- Configure proper CORS
- Use environment variables

But for **local development**, always use **HTTP**.

---

## ✅ Quick Fix Command

```bash
# Stop Angular (Ctrl+C)
# Then run:
ng serve --host 0.0.0.0 --port 4200 --ssl false --disable-host-check
```

This forces HTTP and disables strict host checking for development.
