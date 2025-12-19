# Secure Invite-by-Link: Technical Flow

## Complete Security Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INVITE LINK GENERATION FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

ADMIN/OWNER:
  │
  ├─► POST /groups/{group_id}/generate-invite-link
  │   │
  │   ├─► [JWT Verification]
  │   │   └─► Extract user_id from JWT
  │   │
  │   ├─► [Permission Check]
  │   │   ├─ Query: is_admin_or_owner(group_id, user_id)
  │   │   └─ If false → 403 Forbidden
  │   │
  │   ├─► [Token Generation]
  │   │   │
  │   │   ├─ plain_token = secrets.token_urlsafe(32)
  │   │   │  └─ Result: ~43 characters, 256-bit entropy
  │   │   │
  │   │   ├─ hashed_token = SHA256(plain_token)
  │   │   │  └─ Result: 64 hex characters
  │   │   │
  │   │   └─ expiry = now() + 24 hours
  │   │
  │   ├─► [Database Write]
  │   │   │
  │   │   └─ INSERT INTO memberships {
  │   │       group_id: group_id,
  │   │       user_id: NULL,           ← No user yet!
  │   │       invite_token: hashed_token,  ← Only hash stored!
  │   │       token_expires_at: expiry,
  │   │       role: from_request,
  │   │       status: 'PENDING',
  │   │       invited_by: user_id
  │   │     }
  │   │
  │   └─► [Response to Admin]
  │       │
  │       └─► {
  │           "invite_link": "http://localhost:8080/join-group/1?token={plain_token}",
  │           "expires_at": "2025-12-20T14:30:00",
  │           "group_id": 1
  │         }
  │       
  │       ⚠️  CRITICAL: plain_token only returned here!
  │           Not stored anywhere else!
  │
  └─► Admin copies and shares link


┌─────────────────────────────────────────────────────────────────────────────┐
│                         INVITE LINK REDEMPTION FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

NEW USER (via shared link):
  │
  ├─► Receives link: http://localhost:8080/join-group/1?token={plain_token}
  │
  ├─► Frontend extracts token from URL
  │
  ├─► NEW USER LOGS IN
  │   └─► Receives JWT token
  │
  ├─► POST /groups/1/redeem-invite-link?token={plain_token}
  │   │   Authorization: Bearer {JWT}
  │   │
  │   ├─► [JWT Verification]
  │   │   ├─ Decode JWT
  │   │   ├─ Verify signature
  │   │   └─ Extract user_id, role, expiry
  │   │       If invalid → 401 Unauthorized
  │   │
  │   ├─► [Token Extraction]
  │   │   └─ Get token from query param
  │   │
  │   ├─► [Token Hashing]
  │   │   │
  │   │   └─ provided_hash = SHA256(provided_token)
  │   │       └─ Result: 64 hex characters
  │   │
  │   ├─► [Database Lookup]
  │   │   │
  │   │   └─ SELECT * FROM memberships 
  │   │       WHERE invite_token = provided_hash
  │   │       └─ Result: pending membership record
  │   │
  │   ├─► [Validation Checks]
  │   │   │
  │   │   ├─ [Expiry Check]
  │   │   │  ├─ now() <= token_expires_at?
  │   │   │  └─ If expired → 410 Gone
  │   │   │
  │   │   ├─ [Hash Comparison] (TIMING ATTACK SAFE)
  │   │   │  ├─ secrets.compare_digest(provided_hash, stored_hash)
  │   │   │  ├─ Constant-time comparison
  │   │   │  └─ If mismatch → 404 Not Found
  │   │   │
  │   │   ├─ [Group Match]
  │   │   │  ├─ membership.group_id == requested_group_id?
  │   │   │  └─ If mismatch → 400 Bad Request
  │   │   │
  │   │   └─ [Duplicate Check]
  │   │      ├─ Is user already member of this group?
  │   │      └─ If yes → 409 Conflict
  │   │
  │   ├─► [Membership Redemption]
  │   │   │
  │   │   └─ UPDATE memberships SET {
  │   │       user_id: new_user_id,        ← Claim membership!
  │   │       status: 'ACTIVE',            ← Now active
  │   │       invite_token: NULL,          ← Clear token (one-time use)
  │   │       token_expires_at: NULL
  │   │     } WHERE id = membership_id
  │   │
  │   └─► [Response to User]
  │       │
  │       └─► {
  │           "membership": {
  │             "id": 42,
  │             "group_id": 1,
  │             "user_id": 99,
  │             "role": "member",
  │             "status": "active",
  │             "joined_at": "2025-12-19T14:30:00"
  │           },
  │           "message": "Successfully joined the group!"
  │         }
  │
  └─► User is now ACTIVE member ✅


┌─────────────────────────────────────────────────────────────────────────────┐
│                      SECURITY: ATTACK PREVENTION                            │
└─────────────────────────────────────────────────────────────────────────────┘

Attack: "Token Replay"
├─ Attacker gets token from link
├─ Uses it twice to join group twice
└─ Prevention: ✅ Token cleared after first redemption (one-time use)

Attack: "Token Hijacking from URL"
├─ Attacker intercepts link (plain text)
├─ Uses token before legitimate user
└─ Prevention: ✅ First user to redeem wins (or attacker joins as them)

Attack: "Database Compromise"
├─ Attacker dumps all database tables
├─ Looks at invite_token column
├─ Tries to use hashes in links
└─ Prevention: ✅ SHA256 hashes irreversible, hashes != tokens

Attack: "Timing Attack"
├─ Attacker tries to guess token
├─ Times response differences to narrow down correct token
├─ Finds valid token through timing variations
└─ Prevention: ✅ secrets.compare_digest() constant-time comparison

Attack: "Brute Force Token Guessing"
├─ Attacker tries random tokens
├─ 256-bit entropy = 2^256 possibilities
├─ Brute force infeasible (would take longer than universe age)
└─ Prevention: ✅ Cryptographic entropy too high to guess

Attack: "Man-in-the-Middle"
├─ Attacker intercepts link (plain HTTP)
├─ Steals token
├─ Uses token before user
└─ Prevention: 🔧 Use HTTPS in production (not code-level)

Attack: "Unauthenticated Redemption"
├─ Attacker uses valid token without logging in
├─ Tries to create fake account for group
└─ Prevention: ✅ JWT required (must be logged in to redeem)

Attack: "Privilege Escalation"
├─ Non-admin generates invite links
├─ Creates admin member accounts
└─ Prevention: ✅ is_admin_or_owner() check before generation


┌─────────────────────────────────────────────────────────────────────────────┐
│                        TOKEN LIFECYCLE                                      │
└─────────────────────────────────────────────────────────────────────────────┘

State 1: Generated
  ├─ Plain token: In memory (returned to admin)
  ├─ Hash: In database, associated with PENDING membership
  └─ Status: Can be redeemed

State 2: Shared
  ├─ Plain token: In URL (shared with others)
  ├─ Hash: Still in database
  └─ Status: Can be redeemed

State 3: Redeemed
  ├─ Plain token: Irrelevant (has served its purpose)
  ├─ Hash: CLEARED from database (set to NULL)
  ├─ User ID: NOW populated
  └─ Status: ACTIVE member

State 4: Expired (if not redeemed within 24 hours)
  ├─ Plain token: Useless (outside time window)
  ├─ Hash: Still in database (expired entry)
  ├─ User ID: Still NULL
  └─ Status: PENDING but unusable

Cleanup: Expired entries can be periodically deleted by cron job


┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHY THIS IS SECURE                                       │
└─────────────────────────────────────────────────────────────────────────────┘

✅ Minimum Information Exposure
   - Link contains only token (no user info, group secrets, etc.)
   - Token doesn't encode any sensitive data

✅ No JWT in Link
   - JWT stays in Authorization header (not in URL)
   - JWT is for authentication, token is for authorization
   - Separate concerns, separate security models

✅ Cryptographically Secure
   - Uses Python's `secrets` module (CSPRNG)
   - 256-bit entropy = ~2^256 possible values
   - Cannot be guessed or brute-forced in practice

✅ One-Way Storage
   - Database stores SHA256 hash only
   - Even if database is compromised, original token is unrecoverable
   - Hashes are useless in links (not interchangeable with tokens)

✅ Time-Limited
   - Tokens expire in 24 hours
   - Stale links automatically become invalid
   - Reduces time window for attacks

✅ Single-Use
   - Token cleared immediately after redemption
   - Cannot be reused even if someone has it
   - Prevents multiple join attempts with same link

✅ Timing Attack Safe
   - secrets.compare_digest() uses constant-time comparison
   - Cannot use timing differences to guess tokens
   - All comparisons take same time regardless of match

✅ Authentication Required
   - Redeemer must have valid JWT
   - User must be logged in
   - Prevents anonymous or spoofed account creation

✅ Audit Trail
   - invited_by field records who created link
   - Can track invitation history
   - Useful for security investigations
