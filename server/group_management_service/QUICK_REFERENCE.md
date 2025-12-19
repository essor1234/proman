# Quick Reference: Invite-by-Link Implementation

## 🎯 What Was Built

A **cryptographically secure, zero-exposure invite link system** that allows group admins to generate shareable links for inviting new members without ever exposing sensitive tokens in the database.

## 📋 Changes at a Glance

### New Files
- `app/utils/token_service.py` - Token generation and validation

### Modified Files
1. `app/models/membership.py` - Added `invite_token` and `token_expires_at` fields
2. `app/schemas/membership_schemas.py` - Added `InviteLinkCreate`, `InviteLinkResponse`, `RedeemInviteResponse`
3. `app/repositories/membership_repository.py` - Added token methods
4. `app/controllers/membership_controller.py` - Added link generation/redemption logic
5. `app/routes/invitation_routes.py` - Added two new endpoints

### Documentation Files
- `INVITE_LINK_FEATURE.md` - Complete technical documentation
- `IMPLEMENTATION_SUMMARY.md` - Summary of changes
- `SECURITY_FLOW.md` - Detailed security flow diagrams

## 🔗 New API Endpoints

### 1. Generate Invite Link
```bash
POST /groups/{group_id}/generate-invite-link
Authorization: Bearer {JWT}
Content-Type: application/json

Body: { "role": "member" }

Response:
{
  "invite_link": "http://localhost:8080/join-group/1?token=...",
  "group_id": 1,
  "expires_at": "2025-12-20T14:30:00",
  "message": "Share this link..."
}
```

### 2. Redeem Invite Link
```bash
POST /groups/{group_id}/redeem-invite-link?token={TOKEN}
Authorization: Bearer {JWT}

Response:
{
  "membership": { ... },
  "message": "Successfully joined the group!"
}
```

## 🔒 Security Properties

| Property | Value |
|----------|-------|
| Token Entropy | 256-bit (cryptographically random) |
| Token Storage | SHA256 hash only (irreversible) |
| Token Exposure | Plain token shown only once |
| Expiration | 24 hours |
| Reusability | One-time use (cleared after redemption) |
| Authentication | JWT required |
| Timing Attack Safe | Constant-time comparison |
| DB Compromise Safe | Token unrecoverable from hash |

## 🚀 How to Use

### For Admin/Owner (Generate Link)
1. Call POST `/groups/{groupId}/generate-invite-link`
2. Receive full link in response
3. Share link with someone you want to invite
4. Link valid for 24 hours

### For New User (Redeem Link)
1. Receive link from admin
2. Click link (extracts token from URL)
3. Log in to create account
4. Call POST `/groups/{groupId}/redeem-invite-link?token={TOKEN}`
5. Automatically join group as member

## 🔐 Why This is Secure

✅ **Zero Token Exposure in Database**
- Only SHA256 hash stored
- Original token cannot be recovered

✅ **Cryptographically Secure**
- Uses `secrets.token_urlsafe()` (CSPRNG)
- 256-bit entropy, impossible to brute force

✅ **Time-Limited**
- Expires after 24 hours
- Stale links automatically invalid

✅ **One-Time Use**
- Token cleared after first redemption
- Cannot be reused even if compromised

✅ **Authentication Required**
- User must be logged in (JWT verified)
- Prevents anonymous join attempts

✅ **Timing Attack Prevention**
- Uses `secrets.compare_digest()` for token comparison
- Constant time prevents timing-based attacks

✅ **Separated from JWT**
- Link token ≠ JWT token
- Link is for invitation authorization
- JWT is for user authentication
- Different security models, different concerns

## 📊 Token Lifecycle

```
Generated (admin)
    ↓
    Plain token returned to admin (shown once!)
    Hash stored in database
    ↓
Shared (admin shares link)
    ↓
    Token in URL
    Valid for 24 hours
    ↓
Redeemed (new user clicks link + confirms)
    ↓
    User authenticated via JWT
    Token hash validated
    Membership created
    Hash cleared (one-time use)
    ↓
Active (user is now member)
```

## 🧪 Testing Examples

### Generate Link (as admin with JWT)
```bash
curl -X POST http://localhost:8000/groups/1/generate-invite-link \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"role":"member"}'
```

### Redeem Link (as new user with JWT)
```bash
TOKEN="abc123xyz..."
curl -X POST "http://localhost:8000/groups/1/redeem-invite-link?token=$TOKEN" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## ⚠️ Database Migration Required

Before deploying, run this SQL or use Alembic:

```sql
ALTER TABLE memberships 
ADD COLUMN invite_token VARCHAR(256) UNIQUE NULL,
ADD COLUMN token_expires_at DATETIME NULL;

CREATE INDEX idx_invite_token ON memberships(invite_token);
```

## 📚 More Information

- **Full Technical Docs**: See `INVITE_LINK_FEATURE.md`
- **Security Details**: See `SECURITY_FLOW.md`
- **Implementation Summary**: See `IMPLEMENTATION_SUMMARY.md`

## ✨ Key Highlights

- ✅ No JWT in link (stays in Authorization header)
- ✅ No sensitive data exposed in link
- ✅ Token hashes unrecoverable from database
- ✅ One-time use prevents replay attacks
- ✅ Time-limited prevents stale links being used
- ✅ Constant-time comparison prevents timing attacks
- ✅ Authentication required (JWT verified)
- ✅ Admin-only link generation (permission check)
- ✅ Prevents duplicate memberships
- ✅ Audit trail (tracks who invited)

## 🔄 Migration Checklist

- [ ] Run database migration to add `invite_token` and `token_expires_at` columns
- [ ] Verify `app/utils/token_service.py` is in place
- [ ] Verify all imports in controller/routes are correct
- [ ] Test endpoint: Generate link
- [ ] Test endpoint: Redeem link
- [ ] Test endpoint: Invalid token rejection
- [ ] Test endpoint: Expired token rejection
- [ ] Test endpoint: Duplicate join prevention
- [ ] Test permission check: Non-admin cannot generate
