# Rate Limiting Implementation Guide

## 🔒 Rate Limiting for Non-Staff Users

### Overview
A rate limiting system has been implemented on the login view to prevent brute-force attacks. The system allows a maximum of 5 failed login attempts within a 15-minute window for **non-staff users only**. Staff members and superusers are exempt from rate limiting.

---

## 🎯 Key Features

### 1. **Non-Staff User Protection**
- **Applied to**: Regular students and non-admin users
- **Exempt**: Staff members, superusers, and admin accounts
- **Reason**: Prevent unauthorized access attempts while allowing legitimate admin access

### 2. **Configuration**
```python
LOGIN_ATTEMPTS_LIMIT = 5  # Maximum login attempts
LOGIN_ATTEMPTS_TIMEOUT = 900  # 15 minutes in seconds (900 seconds)
```

### 3. **Rate Limiting Scope**
- **Identifier**: Client IP address (`REMOTE_ADDR`)
- **Cache Backend**: Django's default in-memory cache (LocMemCache)
- **Persistence**: Session-based, cleared after timeout or successful login

---

## 📋 How It Works

### Login Attempt Flow

1. **User enters credentials** → POST request to `/login/`

2. **Check if rate limited**:
   - Get client IP address
   - Look up user account (by username or email)
   - Check if user is staff/superuser
   - If non-staff user, check rate limit

3. **Rate limit check**:
   - If already at 5 failed attempts → Block login, show timeout message
   - Otherwise → Allow login attempt

4. **Authentication**:
   - Verify username/email and password
   - Check account status (active, approved, etc.)

5. **On Success**:
   - Reset failed attempts counter for that IP
   - Create login activity record
   - Set session cookie
   - Redirect to dashboard

6. **On Failure**:
   - Increment failed attempts counter
   - Display remaining attempts (if > 0)
   - Keep user on login page

---

## 🔧 Implementation Details

### Rate Limiting Functions

#### `get_client_ip(request)`
```python
def get_client_ip(request):
    """Get the client IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```
- Extracts client IP considering proxy headers
- Handles X-Forwarded-For from proxies/load balancers

#### `is_rate_limited(identifier)`
```python
def is_rate_limited(identifier):
    """Check if the identifier (IP or username) is rate limited"""
    cache_key = f"{LOGIN_ATTEMPTS_CACHE_KEY_PREFIX}{identifier}"
    attempts = cache.get(cache_key, 0)
    return attempts >= LOGIN_ATTEMPTS_LIMIT
```
- Returns `True` if at or above limit
- Returns `False` if below limit

#### `increment_login_attempts(identifier)`
```python
def increment_login_attempts(identifier):
    """Increment login attempts for the identifier"""
    cache_key = f"{LOGIN_ATTEMPTS_CACHE_KEY_PREFIX}{identifier}"
    attempts = cache.get(cache_key, 0) + 1
    cache.set(cache_key, attempts, LOGIN_ATTEMPTS_TIMEOUT)
```
- Increases attempt counter
- Resets timeout timer on each failure
- Automatically expires after 15 minutes of inactivity

#### `reset_login_attempts(identifier)`
```python
def reset_login_attempts(identifier):
    """Reset login attempts for the identifier (on successful login)"""
    cache_key = f"{LOGIN_ATTEMPTS_CACHE_KEY_PREFIX}{identifier}"
    cache.delete(cache_key)
```
- Clears counter on successful login
- User can immediately attempt again

#### `get_remaining_attempts(identifier)`
```python
def get_remaining_attempts(identifier):
    """Get remaining login attempts for the identifier"""
    cache_key = f"{LOGIN_ATTEMPTS_CACHE_KEY_PREFIX}{identifier}"
    attempts = cache.get(cache_key, 0)
    return max(0, LOGIN_ATTEMPTS_LIMIT - attempts)
```
- Returns remaining attempts (0-5)
- Used for user feedback messages

---

## 📝 User Messages

### Successful Login
```
✓ Welcome back, [First Name]!
```

### Rate Limited (Blocked)
```
✗ Too many failed login attempts. Please try again in 15 minutes.
```

### Failed Attempt (Below Limit)
```
✗ Invalid username/email or password. 4 attempts remaining.
✗ Invalid username/email or password. 3 attempts remaining.
✗ Invalid username/email or password. 2 attempts remaining.
✗ Invalid username/email or password. 1 attempts remaining.
```

### Failed Attempt (At Limit)
```
✗ Invalid username/email or password. Account temporarily locked due to too many failed attempts.
```

### Staff/Admin Attempt
```
✗ Invalid username/email or password.
(No attempt counting shown)
```

---

## 🔐 Security Considerations

### 1. **IP-based Limiting**
- **Advantage**: Prevents distributed attacks from single IP
- **Limitation**: May block multiple users behind NAT
- **Solution**: Users can try again after 15 minutes or use different IP

### 2. **Cache Backend**
- **Current**: LocMemCache (in-memory, single process)
- **Production**: Consider Redis for multi-process deployments
```python
# Redis example for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. **Timing**
- **Attempt Timeout**: 15 minutes (900 seconds)
- **Resets**: On successful login or after 15 minutes
- **Prevents**: Automatic account unlock without admin intervention

### 4. **Admin Exemption**
```python
# Staff/superuser detection
if user_to_check and (user_to_check.is_staff or user_to_check.is_superuser):
    should_rate_limit = False
```
- Admins bypass rate limiting
- Allows system administration without lockout

---

## 📊 Testing Rate Limiting

### Test Case 1: Non-Staff User - Below Limit
1. Open login page
2. Enter non-staff username with wrong password
3. Try 4 times
4. Each attempt shows: "Invalid password. X attempts remaining."
5. **Expected**: All attempts succeed

### Test Case 2: Non-Staff User - At Limit
1. Open login page
2. Enter non-staff username with wrong password
3. Try 5 times
4. 6th attempt shows: "Too many failed login attempts. Please try again in 15 minutes."
5. **Expected**: 6th attempt blocked

### Test Case 3: Admin/Staff User
1. Open login page
2. Enter admin/staff username with wrong password
3. Try unlimited times
4. Shows: "Invalid username/email or password." (no attempt counter)
5. **Expected**: No rate limiting applied

### Test Case 4: Reset After Successful Login
1. Open login page
2. Enter non-staff username with wrong password
3. Try 4 times (4 attempts used)
4. Login with correct password
5. Logout
6. Try again with wrong password
7. Counter resets to 5 remaining attempts
8. **Expected**: Counter resets after successful login

### Test Case 5: Timeout Reset
1. Open login page
2. Enter non-staff username with wrong password
3. Try 5 times (at limit)
4. Wait 15 minutes
5. Try again with wrong password
6. 6th attempt succeeds (gets counted as attempt 1 again)
7. **Expected**: Counter resets after 15-minute timeout

---

## 🛠 Configuration Options

### To Modify Limits
Edit `smru/views.py`:

```python
# Increase limit to 10 attempts
LOGIN_ATTEMPTS_LIMIT = 10

# Change timeout to 30 minutes
LOGIN_ATTEMPTS_TIMEOUT = 1800  # 1800 seconds = 30 minutes
```

### To Switch from IP-based to Username-based
Replace in `login_view()`:
```python
# From:
increment_login_attempts(client_ip)
is_rate_limited(client_ip)
reset_login_attempts(client_ip)

# To:
increment_login_attempts(username_or_email)
is_rate_limited(username_or_email)
reset_login_attempts(username_or_email)
```

### To Enable for All Users (including staff)
Remove staff check in `login_view()`:
```python
# Remove this block:
if user_to_check and (user_to_check.is_staff or user_to_check.is_superuser):
    should_rate_limit = False

# Set to always limit:
should_rate_limit = True
```

---

## 🚀 Production Deployment

### 1. Use Redis for Rate Limiting
```bash
pip install django-redis
```

Update `config/settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 2. Monitor Login Attempts
Add logging to track suspicious activity:
```python
if is_rate_limited(client_ip):
    logger.warning(f"Login rate limit exceeded for IP: {client_ip}")
    # Optional: Send admin alert
```

### 3. Firewall Integration
Consider blocking IPs at firewall level after multiple rate limit hits:
```bash
# Example: Block IP with iptables after 3 rate limit violations
if violations_count >= 3:
    os.system(f"sudo iptables -A INPUT -s {client_ip} -j DROP")
```

---

## 📊 Database Impact

Rate limiting uses Django cache backend, **NOT database**:
- ✓ No database writes for each attempt
- ✓ No additional tables required
- ✓ Minimal performance impact
- ✓ Automatic cleanup after timeout

---

## 🐛 Troubleshooting

### Issue: Rate limit not working
**Cause**: Cache backend not configured
**Solution**: Verify `CACHES` in settings.py is configured

### Issue: Admin users getting rate limited
**Cause**: Admin check failing
**Solution**: Verify user.is_staff or user.is_superuser is set correctly

### Issue: Multiple users on same IP getting blocked
**Cause**: Shared network/NAT behind IP
**Solution**: Use username-based limiting instead of IP-based

### Issue: Rate limit persists after server restart
**Cause**: Cache data persisted
**Solution**: Expected with some cache backends. Manual reset:
```python
from django.core.cache import cache
cache.delete_many([key for key in cache.keys() if 'login_attempts' in key])
```

---

## 📈 Future Enhancements

1. **Adaptive Rate Limiting**
   - Increase limits for known devices
   - Decrease limits for suspicious locations

2. **CAPTCHA Integration**
   - After 3 failed attempts, show CAPTCHA
   - Require CAPTCHA after rate limit

3. **Email Alerts**
   - Notify user of failed login attempts
   - Alert if account locked

4. **Geo-blocking**
   - Block logins from unusual locations
   - Require verification for new locations

5. **2FA Integration**
   - Require 2FA after multiple failed attempts
   - Optional 2FA for sensitive operations

---

## 📚 Related Documentation

- [Django Cache Framework](https://docs.djangoproject.com/en/4.2/topics/cache/)
- [Django Authentication System](https://docs.djangoproject.com/en/4.2/topics/auth/)
- [OWASP Brute Force Prevention](https://owasp.org/www-project-web-security-testing-guide/)

---

**Implementation Date**: May 9, 2026  
**Status**: ✅ Active  
**Environment**: Development & Production Ready