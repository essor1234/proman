# Secure Invite-by-Link Feature

## Overview

A cryptographically secure invite-by-link system for group memberships with **zero token exposure** in the database and **JWT authentication** integration.

## Security Architecture

### 1. **Token Generation & Storage**

```
User Request to Generate Link
    ↓
[TokenService.generate_token()] → 256-bit random token
    ↓
[TokenService.hash_token(token)] → SHA256 hash
    ↓
Store HASH in database (original token NEVER stored)
    ↓
Return invite link with PLAIN TOKEN to user (one-time display)
```

**Why this is secure:**
- Plain token is only shown once to the person generating the link
- If database is compromised, attackers cannot recover the token
- Token is stored as SHA256 hash (one-way function)
- Even with database access, tokens cannot be used

### 2. **Token Redemption**

```
User clicks link with token
    ↓
POST /groups/{group_id}/redeem-invite-link?token={token}
    ↓
[Validate JWT] ← Ensure user is authenticated
    ↓
[TokenService.validate_token()] 
    ├─ Hash provided token
    ├─ Compare hashes using constant-time comparison
    └─ Check token expiry
    ↓
[Redeem] ← Claim membership, clear token (one-time use)
    ↓
User is now ACTIVE member
```

### 3. **JWT Integration**

The system uses JWT for:
- **Authentication verification** - Only logged-in users can redeem links
- **User identification** - JWT payload contains `user_id`
- **No JWT in invite link** - Link token is separate from JWT

Flow:
```
1. User logs in → Receives JWT token
2. User shares invite link (NO JWT included)
3. New user receives link, clicks it
4. New user logs in → Gets their own JWT
5. New user makes POST /redeem-invite-link with:
   - JWT in Authorization header
   - Token from link in query parameter
6. Both are validated, membership is created
```

## API Endpoints

### Generate Invite Link
```
POST /groups/{group_id}/generate-invite-link
Authorization: Bearer {JWT}
Content-Type: application/json

{
  "role": "member"  // or "admin"
}
```

**Response (201 Created):**
```json
{
  "invite_link": "http://localhost:8080/join-group/1?token=abcd1234efgh5678ijkl9012mnop3456",
  "group_id": 1,
  "expires_at": "2025-12-20T14:30:00",
  "message": "Share this link with someone to invite them to the group. Link expires in 24 hours."
}
```

**Security:**
- Only admin/owner can generate links
- Token is cryptographically random (256-bit)
- Token expires in 24 hours
- Only hash stored in database

### Redeem Invite Link
```
POST /groups/{group_id}/redeem-invite-link?token={TOKEN}
Authorization: Bearer {JWT}
```

**Response (200 OK):**
```json
{
  "membership": {
    "id": 42,
    "group_id": 1,
    "user_id": 99,
    "role": "member",
    "status": "active",
    "joined_at": "2025-12-19T14:30:00",
    "updated_at": "2025-12-19T14:30:00"
  },
  "message": "Successfully joined the group!"
}
```

**Security:**
- Requires valid JWT (user must be logged in)
- Token must be valid and not expired (24 hours max)
- Token can only be used once (cleared after redemption)
- Prevents duplicate memberships (user cannot join twice)

## Database Schema Changes

**New columns in `memberships` table:**

```sql
-- Invite link support
invite_token VARCHAR(256) UNIQUE NULLABLE  -- SHA256 hash of token
token_expires_at DATETIME NULLABLE         -- Token expiry timestamp
```

**Migration notes:**
- `user_id` becomes nullable (for link-based invites)
- Token is cleared after redemption (one-time use)
- User_id is populated when link is redeemed

## Implementation Details

### Token Service (`app/utils/token_service.py`)

**Security features:**
- `secrets.token_urlsafe()` - Cryptographically secure random
- `hashlib.sha256()` - One-way hashing
- `secrets.compare_digest()` - Constant-time comparison (prevents timing attacks)
- 24-hour expiration
- One-time use enforcement

### Membership Repository Updates

New methods:
- `create_invite_link()` - Creates pending membership with token
- `get_membership_by_token()` - Finds membership by token hash
- `redeem_invite_link()` - Claims link for user, clears token

### Membership Controller Updates

New methods:
- `generate_invite_link()` - Generates link, validates permissions
- `redeem_invite_link()` - Redeems link, validates expiry & ownership

## Security Checklist

- [x] **Token Entropy** - 256-bit (32 bytes) random tokens
- [x] **Token Storage** - Only SHA256 hash in database
- [x] **Token Exposure** - Plain token only shown once to generator
- [x] **Token Expiry** - 24 hours maximum
- [x] **One-Time Use** - Token cleared after redemption
- [x] **Timing Attack Prevention** - Constant-time comparison
- [x] **JWT Integration** - Authentication verified, not in link
- [x] **Permission Checks** - Only admin/owner can generate
- [x] **Duplicate Prevention** - Cannot join twice
- [x] **DB Compromise** - Token unrecoverable from database

## Usage Examples

### Frontend - Generate Link

```javascript
// User clicks "Generate Invite Link"
const response = await fetch(`http://localhost:3000/groups/1/generate-invite-link`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ role: 'member' })
});

const data = await response.json();
console.log('Share this link:', data.invite_link);
// Expires: data.expires_at
```

### Frontend - Redeem Link

```javascript
// User clicks invite link, gets redirected to join page
// Button handler for "Join Group"
const params = new URLSearchParams(window.location.search);
const token = params.get('token');
const groupId = new URL(window.location.href).pathname.split('/')[2];

const response = await fetch(
  `http://localhost:3000/groups/${groupId}/redeem-invite-link?token=${token}`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`
    }
  }
);

if (response.ok) {
  console.log('Successfully joined!');
  // Redirect to group page
} else {
  console.error('Failed to join:', await response.json());
}
```

## Error Handling

### Invalid Token
```json
{
  "detail": "Invalid or expired token"
}
```
Status: 404 Not Found

### Expired Token
```json
{
  "detail": "Token has expired"
}
```
Status: 410 Gone

### Already Member
```json
{
  "detail": "User is already a member of this group"
}
```
Status: 409 Conflict

### Permission Denied
```json
{
  "detail": "Only admins/owners can generate invite links"
}
```
Status: 403 Forbidden

## Performance Considerations

- Token validation is O(1) - single hash comparison
- Database lookup by token hash is O(log n) - indexed on `invite_token`
- No external API calls required
- Minimal overhead vs. traditional email-based invites

## Future Enhancements

- [ ] Configurable token expiry (not just 24 hours)
- [ ] Token revocation endpoint (before expiry)
- [ ] Link generation audit trail
- [ ] Rate limiting on link generation
- [ ] Custom invite messages
- [ ] Email delivery of invite links
- [ ] QR code generation for links
