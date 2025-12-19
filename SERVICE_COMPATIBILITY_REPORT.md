# ⚠️ Service Compatibility Report

**Date:** December 19, 2025  
**Status:** ⚠️ ISSUES FOUND - ACTION REQUIRED

---

## Summary

**Compatibility Issues:** 5 Major Issues Found  
**Critical:** 2  
**High:** 2  
**Medium:** 1

The new **invite-by-link feature** in `group_management_service` is **NOT fully compatible** with the current service architecture. Several services have **inconsistent JWT/authentication implementations**.

---

## 🔴 Critical Issues

### Issue #1: Inconsistent JWT Implementation

**Services:**
- ✅ `group_management_service` - Uses JWT with `jose` library (decoded payload)
- ❌ `project_management_service` - Uses simple integer as Bearer token (NOT JWT)
- ❌ `account_management_service` - Does NOT validate JWT at all (register/login only)

**Problem:**
```python
# group_management_service (CORRECT - Uses JWT)
from jose import jwt
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
user_id = payload.get("user_id")

# project_management_service (WRONG - Simple integer)
user_id = int(token)  # Assumes token is just a number!

# account_management_service (MISSING - No validation)
# No authentication check on endpoints that need it
```

**Impact:** Group invite links won't work properly when accessed from other services because:
- Project service won't recognize JWT tokens
- Account service has no protected endpoints
- Gateway routes requests but doesn't validate consistently

**Fix Required:** 
```
[ ] Implement JWT validation in project_management_service
[ ] Add JWT validation endpoints in account_management_service
[ ] Standardize SECRET_KEY across all services
```

---

### Issue #2: Inconsistent Database Schema Design

**Current State:**
- `account_management_service` - Uses **SQLModel** (Pydantic + SQLAlchemy hybrid)
- `group_management_service` - Uses **SQLAlchemy ORM**
- `project_management_service` - Uses **SQLAlchemy ORM**
- `folder_and_file_management_service` - Uses **SQLAlchemy ORM**

**Problem:**
```python
# account_management_service
from sqlmodel import SQLModel, Session  # Different ORM!

# Others
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String  # Standard ORM
```

**Impact:**
- Makes data model sharing difficult
- Each service has incompatible model definitions
- Inter-service communication requires manual translation
- Group management uses different patterns than account service

**Fix Required:**
```
[ ] Migrate account_management_service to SQLAlchemy
[ ] OR migrate all services to SQLModel
[ ] Standardize on one ORM across all services
```

---

## 🟠 High Priority Issues

### Issue #3: Security Module Missing in File Service

**File Service Location:** `server/folder_and_file_management_service/app/core/`

**Status:**
```
❌ /core/security.py - NOT FOUND
✅ /core/database.py - EXISTS
```

**Problem:** File management service has no security module, but will likely need to validate users when file operations are performed.

**Impact:** 
- Cannot implement file access control
- No user authentication for uploads/downloads
- No JWT validation

**Fix Required:**
```
[ ] Create security.py in file_management_service
[ ] Implement JWT validation matching group_management_service
[ ] Add file ownership validation
```

---

### Issue #4: Missing JWT Configuration Environment Variables

**Current State:**
```
group_management_service:
  ✅ JWT_SECRET from os.environ.get("JWT_SECRET", "my_very_secret_jwt_key")
  
project_management_service:
  ❌ No JWT support (commented out)
  
account_management_service:
  ❌ No JWT support

gateway:
  ❌ No JWT validation, just proxies requests
```

**Problem:** 
- Services use different/missing JWT secrets
- No centralized secret management
- Invite links can't be validated across service boundaries

**Fix Required:**
```
[ ] Add JWT_SECRET to docker-compose.yaml environment
[ ] Ensure all services use same secret
[ ] Add JWT_ALGORITHM as env variable
[ ] Update gateway to validate JWT before routing
```

---

## 🟡 Medium Priority Issue

### Issue #5: Gateway Does Not Validate JWT

**Current Implementation:**
```python
# gateway/app/routes/gatewayRouter.py
@router.post("/user")
async def user(request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    # ⚠️ Just forwards the header, doesn't validate!
    resp = await client.get(
        f"{ACCOUNT_SERVICE_URL}/users/me",
        headers=forward_headers,
        timeout=10.0,
    )
    return Response(content=resp.text, ...)
```

**Problem:**
- Gateway forwards JWT without validation
- Invalid/expired tokens reach backend services
- No centralized auth layer
- Inconsistent handling across endpoints

**Fix Required:**
```
[ ] Add JWT validation middleware in gateway
[ ] Reject invalid tokens at gateway level
[ ] Forward only validated claims to backend
```

---

## ✅ Compatibility Matrix

| Service | JWT | DB ORM | Security | Tested |
|---------|-----|--------|----------|--------|
| group_management | ✅ | SQLAlchemy | ✅ jose | ❓ |
| project_management | ❌ | SQLAlchemy | ❌ int-only | ❌ |
| account_management | ❌ | SQLModel | ❌ none | ❌ |
| file_management | ❌ | SQLAlchemy | ❌ none | ❌ |
| gateway | ⚠️ | - | ❌ proxy-only | ❌ |

---

## 🔧 Recommended Fix Order

### Phase 1: Critical (Do First)
1. **Standardize JWT across all services**
   - Update `project_management_service` to use JWT validation
   - Update `account_management_service` to use JWT
   - Use consistent `SECRET_KEY` and `ALGORITHM`

2. **Add JWT to gateway**
   - Validate JWT before routing
   - Extract claims for backend
   - Reject invalid tokens early

### Phase 2: High Priority (Do Next)
3. **Create missing security module**
   - Add `security.py` to file_management_service
   - Implement JWT validation

4. **Standardize ORM**
   - Decide: SQLModel or SQLAlchemy
   - Migrate account_management_service

### Phase 3: Medium Priority (Do Later)
5. **Environment configuration**
   - Centralize JWT_SECRET in docker-compose
   - Add to all services
   - Consistent across containers

---

## 🚀 Invite-by-Link Compatibility Status

**With current services:** ⚠️ NOT COMPATIBLE

**Invite link flow would fail at:**
1. ❌ Generating link (group service needs JWT from user)
2. ❌ Redeeming link (other services don't validate JWT correctly)
3. ❌ Cross-service validation (no consistent auth)

**Will work after Phase 1 fixes:** ✅ YES

---

## 📋 Action Items

### For Account Management Service
```python
# Current - Missing JWT
@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return {"user_id": user.id}  # ❌ Should return JWT!

# Should be:
def login(...):
    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}
```

### For Project Management Service
```python
# Current - Uses integer as token
user_id = int(token)  # ❌ WRONG

# Should be:
from jose import jwt
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
user_id = payload.get("user_id")  # ✅ CORRECT
```

### For File Management Service
```python
# Missing entirely
# Add: app/core/security.py
# Copy from group_management_service and adapt
```

### For Gateway
```python
# Current - Proxies without validation
headers["Authorization"] = request.headers["authorization"]

# Should add:
# 1. Decode JWT
# 2. Validate signature
# 3. Check expiration
# 4. Forward only if valid
```

---

## 📝 Implementation Checklist

### Standardize JWT Implementation
- [ ] Define shared JWT_SECRET (environment variable)
- [ ] Define shared JWT_ALGORITHM (HS256)
- [ ] Create shared token creation utility
- [ ] Create shared token validation utility

### Update Each Service

**group_management_service:**
- [x] ✅ Already has JWT validation

**account_management_service:**
- [ ] Import JWT library (jose)
- [ ] Add token creation function
- [ ] Return JWT on login
- [ ] Update login endpoint
- [ ] Test JWT validation

**project_management_service:**
- [ ] Import JWT library (jose)
- [ ] Replace integer token with JWT validation
- [ ] Update get_current_user() function
- [ ] Update security.py
- [ ] Test JWT validation

**file_management_service:**
- [ ] Create security.py module
- [ ] Copy JWT validation from group service
- [ ] Add to all protected routes
- [ ] Test JWT validation

**gateway:**
- [ ] Add JWT validation middleware
- [ ] Validate before routing
- [ ] Reject expired tokens
- [ ] Forward only validated tokens
- [ ] Test all routes

---

## 🧪 Testing After Fixes

```bash
# Test 1: Generate JWT from account service
curl -X POST http://localhost:8001/auth/login \
  -d "username=test&password=test" \
  -H "Content-Type: application/x-www-form-urlencoded"
# Should return: {"access_token": "eyJ...", "token_type": "bearer"}

# Test 2: Use JWT on group service
curl -X POST http://localhost:8002/groups/1/generate-invite-link \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"role":"member"}'
# Should work

# Test 3: Use JWT on project service
curl -X GET http://localhost:8003/projects \
  -H "Authorization: Bearer {JWT_TOKEN}"
# Should work

# Test 4: Invalid JWT rejected
curl -X POST http://localhost:8002/groups/1/generate-invite-link \
  -H "Authorization: Bearer invalid_token"
# Should return: 401 Unauthorized
```

---

## 🎯 Current Recommendation

### ⛔ DO NOT deploy invite-by-link feature yet

The new feature **will not work correctly** across services due to inconsistent JWT implementation.

### ✅ DO THIS FIRST

1. **Implement JWT in account_management_service** (1-2 hours)
2. **Update project_management_service to use JWT** (1-2 hours)
3. **Add security to file_management_service** (1 hour)
4. **Add JWT validation to gateway** (1-2 hours)
5. **Test all services** (1-2 hours)

**Total time: 5-9 hours**

Then deploy invite-by-link feature ✅

---

## 📞 Summary

**Invite-by-link is implemented correctly** ✅ in group_management_service.

**BUT** other services aren't compatible yet ⚠️.

**To fix:** Standardize JWT across all services (5-9 hours of work).

After that, everything will work together seamlessly! 🚀
