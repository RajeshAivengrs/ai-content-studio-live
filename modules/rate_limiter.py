"""
AI Content Studio - Rate Limiter Module
Handles API rate limiting and throttling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.user_limits = defaultdict(lambda: deque())
        self.endpoint_limits = {
            "script_generation": {"requests": 10, "window": 3600},  # 10 per hour
            "video_creation": {"requests": 5, "window": 3600},      # 5 per hour
            "api_call": {"requests": 100, "window": 3600}           # 100 per hour
        }
    
    async def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """Check if user has exceeded rate limit"""
        try:
            limit_config = self.endpoint_limits.get(endpoint, {"requests": 100, "window": 3600})
            max_requests = limit_config["requests"]
            window_seconds = limit_config["window"]
            
            now = datetime.utcnow()
            cutoff_time = now - timedelta(seconds=window_seconds)
            
            # Get user's request history
            user_requests = self.user_limits[user_id]
            
            # Remove old requests
            while user_requests and user_requests[0] < cutoff_time:
                user_requests.popleft()
            
            # Check if limit exceeded
            if len(user_requests) >= max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id} on endpoint {endpoint}")
                return False
            
            # Add current request
            user_requests.append(now)
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return True  # Allow on error
