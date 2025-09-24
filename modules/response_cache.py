"""
AI Content Studio - Response Cache Module
Handles response caching for improved performance
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class ResponseCache:
    def __init__(self):
        self.cache = {}
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached response"""
        try:
            if key in self.cache:
                entry = self.cache[key]
                if datetime.utcnow() < entry["expires_at"]:
                    return entry["data"]
                else:
                    del self.cache[key]
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    async def set(self, key: str, data: Any, ttl: int = None) -> bool:
        """Set cached response"""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            self.cache[key] = {
                "data": data,
                "expires_at": expires_at,
                "created_at": datetime.utcnow()
            }
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
