import sqlite3
import urllib.request
import json

# Query group database
conn = sqlite3.connect(r'e:\New folder\proman\server\group_management_service\app\group_service.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name, owner_id FROM groups LIMIT 1')
result = cursor.fetchone()
conn.close()

if result:
    group_id, name, owner_id = result
    print(f"Found group: ID={group_id}, Name={name}, Owner={owner_id}")
    
    # Test GET /groups/{id}
    url = f"http://localhost:8003/groups/{group_id}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"\nGET {url}")
            print(f"Status: {response.status}")
            print(f"Response:\n{json.dumps(data, indent=2)}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No groups found in database")
