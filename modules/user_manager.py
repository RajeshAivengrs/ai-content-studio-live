"""
AI Content Studio - User Manager Module
Handles user management, profiles, and authentication
"""

import asyncio
import json
import logging
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import bcrypt
import jwt
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    name: str
    subscription_plan: str
    created_at: datetime
    last_login: Optional[datetime] = None
    profile_data: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}
    usage_stats: Dict[str, Any] = {}

class UserManager:
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.jwt_algorithm = "HS256"
        self.jwt_expiry = timedelta(hours=24)
        self.subscription_plans = self._load_subscription_plans()
        self.user_cache = {}
        
    def _load_subscription_plans(self) -> Dict[str, Any]:
        """Load subscription plans"""
        return {
            "free": {
                "name": "Free",
                "price": 0,
                "currency": "USD",
                "limits": {
                    "scripts_per_month": 5,
                    "videos_per_month": 2,
                    "storage_gb": 1,
                    "api_calls_per_day": 100
                },
                "features": [
                    "Basic script generation",
                    "Standard video creation",
                    "Email support"
                ]
            },
            "pro": {
                "name": "Pro",
                "price": 29,
                "currency": "USD",
                "limits": {
                    "scripts_per_month": 50,
                    "videos_per_month": 20,
                    "storage_gb": 10,
                    "api_calls_per_day": 1000
                },
                "features": [
                    "Advanced script generation",
                    "HD video creation",
                    "Voice cloning",
                    "Priority support",
                    "Analytics dashboard"
                ]
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 99,
                "currency": "USD",
                "limits": {
                    "scripts_per_month": 500,
                    "videos_per_month": 200,
                    "storage_gb": 100,
                    "api_calls_per_day": 10000
                },
                "features": [
                    "Unlimited script generation",
                    "4K video creation",
                    "Custom voice training",
                    "Dedicated support",
                    "Advanced analytics",
                    "API access",
                    "White-label options"
                ]
            }
        }
    
    async def create_user(
        self,
        email: str,
        password: str,
        name: str,
        subscription_plan: str = "free"
    ) -> Dict[str, Any]:
        """Create new user"""
        try:
            # Validate inputs
            if not email or not password or not name:
                raise ValueError("Email, password, and name are required")
            
            if subscription_plan not in self.subscription_plans:
                subscription_plan = "free"
            
            # Check if user already exists
            existing_user = await self._get_user_by_email(email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Generate user ID
            user_id = self._generate_user_id(email)
            
            # Hash password
            hashed_password = self._hash_password(password)
            
            # Create user profile
            user_profile = UserProfile(
                user_id=user_id,
                email=email,
                name=name,
                subscription_plan=subscription_plan,
                created_at=datetime.utcnow(),
                profile_data={
                    "avatar_url": "",
                    "bio": "",
                    "website": "",
                    "social_links": {}
                },
                preferences={
                    "default_script_style": "professional",
                    "default_video_style": "professional",
                    "default_voice": "professional_male",
                    "notifications": {
                        "email": True,
                        "push": True,
                        "sms": False
                    },
                    "privacy": {
                        "profile_public": False,
                        "content_public": False
                    }
                },
                usage_stats={
                    "scripts_generated": 0,
                    "videos_created": 0,
                    "api_calls_made": 0,
                    "storage_used_gb": 0.0,
                    "last_reset": datetime.utcnow().isoformat()
                }
            )
            
            # Save user
            await self._save_user(user_profile)
            
            # Generate JWT token
            token = self._generate_jwt_token(user_profile)
            
            logger.info(f"Created user {user_id} with email {email}")
            
            return {
                "user_id": user_id,
                "email": email,
                "name": name,
                "subscription_plan": subscription_plan,
                "token": token,
                "created_at": user_profile.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user"""
        try:
            # Get user by email
            user = await self._get_user_by_email(email)
            if not user:
                raise ValueError("Invalid email or password")
            
            # Verify password
            if not self._verify_password(password, user["hashed_password"]):
                raise ValueError("Invalid email or password")
            
            # Update last login
            await self._update_last_login(user["user_id"])
            
            # Generate new token
            token = self._generate_jwt_token(user)
            
            logger.info(f"User {user['user_id']} authenticated successfully")
            
            return {
                "user_id": user["user_id"],
                "email": user["email"],
                "name": user["name"],
                "subscription_plan": user["subscription_plan"],
                "token": token,
                "last_login": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get subscription plan details
            plan_details = self.subscription_plans.get(user["subscription_plan"], {})
            
            return {
                "user_id": user["user_id"],
                "email": user["email"],
                "name": user["name"],
                "subscription_plan": user["subscription_plan"],
                "plan_details": plan_details,
                "created_at": user["created_at"],
                "last_login": user.get("last_login"),
                "profile_data": user.get("profile_data", {}),
                "preferences": user.get("preferences", {}),
                "usage_stats": user.get("usage_stats", {}),
                "usage_limits": plan_details.get("limits", {}),
                "features": plan_details.get("features", [])
            }
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user profile"""
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Validate updates
            allowed_fields = [
                "name", "profile_data", "preferences"
            ]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    user[field] = value
                else:
                    logger.warning(f"Attempted to update restricted field: {field}")
            
            # Save updated user
            await self._save_user(user)
            
            logger.info(f"Updated profile for user {user_id}")
            
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise
    
    async def change_subscription_plan(
        self,
        user_id: str,
        new_plan: str
    ) -> Dict[str, Any]:
        """Change user subscription plan"""
        try:
            if new_plan not in self.subscription_plans:
                raise ValueError("Invalid subscription plan")
            
            user = await self._get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            old_plan = user["subscription_plan"]
            user["subscription_plan"] = new_plan
            
            # Save updated user
            await self._save_user(user)
            
            logger.info(f"Changed subscription plan for user {user_id} from {old_plan} to {new_plan}")
            
            return {
                "user_id": user_id,
                "old_plan": old_plan,
                "new_plan": new_plan,
                "plan_details": self.subscription_plans[new_plan],
                "changed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error changing subscription plan: {str(e)}")
            raise
    
    async def update_usage_stats(
        self,
        user_id: str,
        stats_update: Dict[str, Any]
    ):
        """Update user usage statistics"""
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return
            
            usage_stats = user.get("usage_stats", {})
            
            for key, value in stats_update.items():
                if key in usage_stats:
                    if isinstance(usage_stats[key], (int, float)):
                        usage_stats[key] += value
                    else:
                        usage_stats[key] = value
                else:
                    usage_stats[key] = value
            
            user["usage_stats"] = usage_stats
            await self._save_user(user)
            
        except Exception as e:
            logger.error(f"Error updating usage stats: {str(e)}")
    
    async def check_usage_limits(self, user_id: str, action: str) -> bool:
        """Check if user has exceeded usage limits"""
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return False
            
            plan = user["subscription_plan"]
            plan_details = self.subscription_plans.get(plan, {})
            limits = plan_details.get("limits", {})
            usage_stats = user.get("usage_stats", {})
            
            # Check specific limits
            if action == "script_generation":
                limit = limits.get("scripts_per_month", 0)
                used = usage_stats.get("scripts_generated", 0)
                return used < limit
            
            elif action == "video_creation":
                limit = limits.get("videos_per_month", 0)
                used = usage_stats.get("videos_created", 0)
                return used < limit
            
            elif action == "api_call":
                limit = limits.get("api_calls_per_day", 0)
                used = usage_stats.get("api_calls_made", 0)
                return used < limit
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking usage limits: {str(e)}")
            return False
    
    def _generate_user_id(self, email: str) -> str:
        """Generate unique user ID"""
        content = f"{email}_{datetime.utcnow().isoformat()}_{secrets.token_hex(8)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _generate_jwt_token(self, user: Dict[str, Any]) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": user["user_id"],
            "email": user["email"],
            "subscription_plan": user["subscription_plan"],
            "exp": datetime.utcnow() + self.jwt_expiry,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    async def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        # In a real implementation, this would query the database
        # For now, return a mock user
        return {
            "user_id": user_id,
            "email": "user@example.com",
            "name": "Test User",
            "subscription_plan": "pro",
            "created_at": datetime.utcnow().isoformat(),
            "hashed_password": "$2b$12$mock_hash",
            "profile_data": {},
            "preferences": {},
            "usage_stats": {
                "scripts_generated": 0,
                "videos_created": 0,
                "api_calls_made": 0
            }
        }
    
    async def _get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        # In a real implementation, this would query the database
        return None
    
    async def _save_user(self, user: Dict[str, Any]):
        """Save user to database"""
        # In a real implementation, this would save to database
        logger.info(f"Saving user {user['user_id']}")
    
    async def _update_last_login(self, user_id: str):
        """Update user's last login time"""
        # In a real implementation, this would update the database
        logger.info(f"Updated last login for user {user_id}")
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return {}
            
            usage_stats = user.get("usage_stats", {})
            plan_details = self.subscription_plans.get(user["subscription_plan"], {})
            limits = plan_details.get("limits", {})
            
            return {
                "user_id": user_id,
                "subscription_plan": user["subscription_plan"],
                "usage": usage_stats,
                "limits": limits,
                "usage_percentage": {
                    "scripts": (usage_stats.get("scripts_generated", 0) / max(1, limits.get("scripts_per_month", 1))) * 100,
                    "videos": (usage_stats.get("videos_created", 0) / max(1, limits.get("videos_per_month", 1))) * 100,
                    "api_calls": (usage_stats.get("api_calls_made", 0) / max(1, limits.get("api_calls_per_day", 1))) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {}
