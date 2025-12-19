"""
Redis caching utility for user data
"""
import redis
import json
import os
from typing import Optional, Dict, List
from datetime import timedelta

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = 300  # 5 minutes

class UserCache:
    """Cache layer for user data"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            self.enabled = True
            print("✅ Redis cache connected")
        except Exception as e:
            print(f"⚠️  Redis cache unavailable: {e}. Operating without cache.")
            self.enabled = False
            self.redis_client = None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get cached user by ID"""
        if not self.enabled:
            return None
        
        try:
            key = f"user:{user_id}"
            data = self.redis_client.get(key)
            if data:
                print(f"💾 Cache hit: {key}")
                return json.loads(data)
            return None
        except Exception as e:
            print(f"⚠️  Cache get error: {e}")
            return None
    
    def set_user(self, user_id: int, data: Dict, ttl: int = CACHE_TTL):
        """Cache user data"""
        if not self.enabled:
            return
        
        try:
            key = f"user:{user_id}"
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(data)
            )
            print(f"💾 Cached: {key}")
        except Exception as e:
            print(f"⚠️  Cache set error: {e}")
    
    def get_users_batch(self, user_ids: List[int]) -> Dict[str, Dict]:
        """Get multiple cached users"""
        if not self.enabled:
            return {}
        
        try:
            result = {}
            for user_id in user_ids:
                key = f"user:{user_id}"
                data = self.redis_client.get(key)
                if data:
                    result[str(user_id)] = json.loads(data)
            
            if result:
                print(f"💾 Cache hits for {len(result)}/{len(user_ids)} users")
            return result
        except Exception as e:
            print(f"⚠️  Cache batch get error: {e}")
            return {}
    
    def set_users_batch(self, users: Dict[str, Dict], ttl: int = CACHE_TTL):
        """Cache multiple users"""
        if not self.enabled:
            return
        
        try:
            for user_id_str, data in users.items():
                key = f"user:{user_id_str}"
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(data)
                )
            print(f"💾 Cached {len(users)} users")
        except Exception as e:
            print(f"⚠️  Cache batch set error: {e}")
    
    def invalidate_user(self, user_id: int):
        """Remove user from cache"""
        if not self.enabled:
            return
        
        try:
            key = f"user:{user_id}"
            self.redis_client.delete(key)
            print(f"🗑️  Invalidated cache: {key}")
        except Exception as e:
            print(f"⚠️  Cache invalidate error: {e}")

# Global cache instance
cache = UserCache()
