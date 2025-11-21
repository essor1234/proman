import sqlite3

print("\n" + "="*60)
print("ACCOUNT SERVICE DATABASE (User Database)")
print("="*60)
print("Location: server/account_management_service/data/app.db\n")

try:
    conn = sqlite3.connect('server/account_management_service/data/app.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("📋 USERS TABLE:")
    cursor.execute('SELECT id, username, email, full_name FROM users;')
    users = cursor.fetchall()
    if users:
        for user in users:
            print(f"  ID: {user['id']}")
            print(f"  Username: {user['username']}")
            print(f"  Email: {user['email']}")
            print(f"  Full Name: {user['full_name']}")
            print()
    else:
        print("  (No users found)")
    
    conn.close()
except Exception as e:
    print(f"Error reading Account database: {e}")

print("\n" + "="*60)
print("GROUP SERVICE DATABASE (Group Database)")
print("="*60)
print("Location: Inside docker container at /app/group_service.db\n")

# Query group database inside container
import subprocess
import json

query_groups = """
import sqlite3
import json

conn = sqlite3.connect('/app/group_service.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get groups
cursor.execute('SELECT id, name, owner_id, visibility FROM groups;')
groups = [dict(row) for row in cursor.fetchall()]

# Get memberships
cursor.execute('SELECT id, group_id, user_id, role FROM memberships;')
memberships = [dict(row) for row in cursor.fetchall()]

print(json.dumps({'groups': groups, 'memberships': memberships}))
conn.close()
"""

try:
    result = subprocess.run(
        ['docker', 'exec', 'group_service', 'python3', '-c', query_groups],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout.strip())
        
        print("📋 GROUPS TABLE:")
        for group in data['groups']:
            print(f"  ID: {group['id']}")
            print(f"  Name: {group['name']}")
            print(f"  Owner ID: {group['owner_id']}")
            print(f"  Visibility: {group['visibility']}")
            print()
        
        print("📋 MEMBERSHIPS TABLE:")
        for member in data['memberships']:
            print(f"  Membership ID: {member['id']}")
            print(f"  Group ID: {member['group_id']}")
            print(f"  User ID: {member['user_id']}")
            print(f"  Role: {member['role']}")
            print()
    else:
        print(f"Error: {result.stderr}")
except Exception as e:
    print(f"Error reading Group database: {e}")

print("="*60)
print("\n✨ KEY INSIGHT:")
print("  Account Service stores: user IDs, names, emails")
print("  Group Service stores: user IDs ONLY (not names/emails)")
print("  When you ask for members, Group Service calls Account Service")
print("  to get the full user details!")
print("="*60)
