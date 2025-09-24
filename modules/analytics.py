"""
AI Content Studio - Analytics Module
Handles analytics, metrics, and reporting
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)

class Analytics:
    def __init__(self):
        self.metrics_store = defaultdict(list)
        self.user_metrics = defaultdict(dict)
        self.system_metrics = {
            "total_requests": 0,
            "total_scripts_generated": 0,
            "total_videos_created": 0,
            "total_users": 0,
            "average_response_time": 0.0,
            "error_rate": 0.0,
            "uptime": datetime.utcnow()
        }
        
    async def track_script_generation(self, user_id: str, metadata: Dict[str, Any] = None):
        """Track script generation event"""
        try:
            event = {
                "event_type": "script_generation",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            self.metrics_store["script_generations"].append(event)
            self.system_metrics["total_scripts_generated"] += 1
            
            # Update user metrics
            if user_id not in self.user_metrics:
                self.user_metrics[user_id] = {
                    "scripts_generated": 0,
                    "videos_created": 0,
                    "api_calls": 0,
                    "last_activity": datetime.utcnow().isoformat()
                }
            
            self.user_metrics[user_id]["scripts_generated"] += 1
            self.user_metrics[user_id]["last_activity"] = datetime.utcnow().isoformat()
            
            logger.info(f"Tracked script generation for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking script generation: {str(e)}")
    
    async def track_video_creation(self, user_id: str, metadata: Dict[str, Any] = None):
        """Track video creation event"""
        try:
            event = {
                "event_type": "video_creation",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            self.metrics_store["video_creations"].append(event)
            self.system_metrics["total_videos_created"] += 1
            
            # Update user metrics
            if user_id not in self.user_metrics:
                self.user_metrics[user_id] = {
                    "scripts_generated": 0,
                    "videos_created": 0,
                    "api_calls": 0,
                    "last_activity": datetime.utcnow().isoformat()
                }
            
            self.user_metrics[user_id]["videos_created"] += 1
            self.user_metrics[user_id]["last_activity"] = datetime.utcnow().isoformat()
            
            logger.info(f"Tracked video creation for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking video creation: {str(e)}")
    
    async def track_social_publish(self, user_id: str, metadata: Dict[str, Any] = None):
        """Track social media publishing event"""
        try:
            event = {
                "event_type": "social_publish",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            self.metrics_store["social_publishes"].append(event)
            
            logger.info(f"Tracked social publish for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking social publish: {str(e)}")
    
    async def track_api_call(self, user_id: str, endpoint: str, response_time: float, status_code: int):
        """Track API call"""
        try:
            event = {
                "event_type": "api_call",
                "user_id": user_id,
                "endpoint": endpoint,
                "response_time": response_time,
                "status_code": status_code,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.metrics_store["api_calls"].append(event)
            self.system_metrics["total_requests"] += 1
            
            # Update user metrics
            if user_id not in self.user_metrics:
                self.user_metrics[user_id] = {
                    "scripts_generated": 0,
                    "videos_created": 0,
                    "api_calls": 0,
                    "last_activity": datetime.utcnow().isoformat()
                }
            
            self.user_metrics[user_id]["api_calls"] += 1
            self.user_metrics[user_id]["last_activity"] = datetime.utcnow().isoformat()
            
            # Update system metrics
            self._update_system_metrics(response_time, status_code)
            
        except Exception as e:
            logger.error(f"Error tracking API call: {str(e)}")
    
    def _update_system_metrics(self, response_time: float, status_code: int):
        """Update system-level metrics"""
        try:
            # Update average response time
            current_avg = self.system_metrics["average_response_time"]
            total_requests = self.system_metrics["total_requests"]
            
            if total_requests > 0:
                new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
                self.system_metrics["average_response_time"] = round(new_avg, 3)
            
            # Update error rate
            error_requests = len([call for call in self.metrics_store["api_calls"] 
                                if call["status_code"] >= 400])
            self.system_metrics["error_rate"] = round(
                (error_requests / max(1, total_requests)) * 100, 2
            )
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {str(e)}")
    
    async def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get analytics dashboard data for user"""
        try:
            user_metrics = self.user_metrics.get(user_id, {})
            
            # Get user's recent activity
            recent_scripts = [
                event for event in self.metrics_store["script_generations"]
                if event["user_id"] == user_id
            ][-10:]  # Last 10 scripts
            
            recent_videos = [
                event for event in self.metrics_store["video_creations"]
                if event["user_id"] == user_id
            ][-10:]  # Last 10 videos
            
            # Calculate trends
            trends = await self._calculate_user_trends(user_id)
            
            # Get system-wide stats
            system_stats = await self._get_system_stats()
            
            return {
                "user_id": user_id,
                "user_metrics": user_metrics,
                "recent_activity": {
                    "scripts": recent_scripts,
                    "videos": recent_videos
                },
                "trends": trends,
                "system_stats": system_stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {}
    
    async def get_usage_data(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics for user"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Filter events by date and user
            user_scripts = [
                event for event in self.metrics_store["script_generations"]
                if (event["user_id"] == user_id and 
                    datetime.fromisoformat(event["timestamp"]) >= cutoff_date)
            ]
            
            user_videos = [
                event for event in self.metrics_store["video_creations"]
                if (event["user_id"] == user_id and 
                    datetime.fromisoformat(event["timestamp"]) >= cutoff_date)
            ]
            
            user_api_calls = [
                event for event in self.metrics_store["api_calls"]
                if (event["user_id"] == user_id and 
                    datetime.fromisoformat(event["timestamp"]) >= cutoff_date)
            ]
            
            # Calculate daily usage
            daily_usage = self._calculate_daily_usage(user_scripts, user_videos, user_api_calls, days)
            
            # Calculate usage patterns
            usage_patterns = self._calculate_usage_patterns(user_scripts, user_videos, user_api_calls)
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_scripts": len(user_scripts),
                "total_videos": len(user_videos),
                "total_api_calls": len(user_api_calls),
                "daily_usage": daily_usage,
                "usage_patterns": usage_patterns,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting usage data: {str(e)}")
            return {}
    
    async def _calculate_user_trends(self, user_id: str) -> Dict[str, Any]:
        """Calculate user trends"""
        try:
            # Get last 30 days of data
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            recent_scripts = [
                event for event in self.metrics_store["script_generations"]
                if (event["user_id"] == user_id and 
                    datetime.fromisoformat(event["timestamp"]) >= cutoff_date)
            ]
            
            recent_videos = [
                event for event in self.metrics_store["video_creations"]
                if (event["user_id"] == user_id and 
                    datetime.fromisoformat(event["timestamp"]) >= cutoff_date)
            ]
            
            # Calculate trends
            script_trend = self._calculate_trend(recent_scripts, 30)
            video_trend = self._calculate_trend(recent_videos, 30)
            
            return {
                "script_generation_trend": script_trend,
                "video_creation_trend": video_trend,
                "activity_score": self._calculate_activity_score(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error calculating user trends: {str(e)}")
            return {}
    
    def _calculate_trend(self, events: List[Dict], days: int) -> str:
        """Calculate trend direction"""
        if len(events) < 2:
            return "stable"
        
        # Split into two halves
        mid_point = len(events) // 2
        first_half = events[:mid_point]
        second_half = events[mid_point:]
        
        first_count = len(first_half)
        second_count = len(second_half)
        
        if second_count > first_count * 1.2:
            return "increasing"
        elif second_count < first_count * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_activity_score(self, user_id: str) -> float:
        """Calculate user activity score"""
        try:
            user_metrics = self.user_metrics.get(user_id, {})
            
            scripts = user_metrics.get("scripts_generated", 0)
            videos = user_metrics.get("videos_created", 0)
            api_calls = user_metrics.get("api_calls", 0)
            
            # Weighted score
            score = (scripts * 2) + (videos * 3) + (api_calls * 0.1)
            
            # Normalize to 0-100
            return min(100, max(0, score))
            
        except Exception as e:
            logger.error(f"Error calculating activity score: {str(e)}")
            return 0.0
    
    def _calculate_daily_usage(self, scripts: List, videos: List, api_calls: List, days: int) -> List[Dict]:
        """Calculate daily usage statistics"""
        try:
            daily_usage = []
            
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                
                day_scripts = len([
                    s for s in scripts 
                    if datetime.fromisoformat(s["timestamp"]).date() == date.date()
                ])
                
                day_videos = len([
                    v for v in videos 
                    if datetime.fromisoformat(v["timestamp"]).date() == date.date()
                ])
                
                day_api_calls = len([
                    a for a in api_calls 
                    if datetime.fromisoformat(a["timestamp"]).date() == date.date()
                ])
                
                daily_usage.append({
                    "date": date_str,
                    "scripts": day_scripts,
                    "videos": day_videos,
                    "api_calls": day_api_calls
                })
            
            return list(reversed(daily_usage))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error calculating daily usage: {str(e)}")
            return []
    
    def _calculate_usage_patterns(self, scripts: List, videos: List, api_calls: List) -> Dict[str, Any]:
        """Calculate usage patterns"""
        try:
            all_events = scripts + videos + api_calls
            
            if not all_events:
                return {}
            
            # Calculate hourly patterns
            hourly_counts = Counter()
            for event in all_events:
                hour = datetime.fromisoformat(event["timestamp"]).hour
                hourly_counts[hour] += 1
            
            # Calculate day of week patterns
            weekday_counts = Counter()
            for event in all_events:
                weekday = datetime.fromisoformat(event["timestamp"]).weekday()
                weekday_counts[weekday] += 1
            
            return {
                "peak_hour": hourly_counts.most_common(1)[0][0] if hourly_counts else 0,
                "peak_day": weekday_counts.most_common(1)[0][0] if weekday_counts else 0,
                "hourly_distribution": dict(hourly_counts),
                "weekly_distribution": dict(weekday_counts)
            }
            
        except Exception as e:
            logger.error(f"Error calculating usage patterns: {str(e)}")
            return {}
    
    async def _get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        try:
            total_users = len(self.user_metrics)
            self.system_metrics["total_users"] = total_users
            
            # Calculate uptime
            uptime = datetime.utcnow() - self.system_metrics["uptime"]
            
            return {
                "total_requests": self.system_metrics["total_requests"],
                "total_scripts_generated": self.system_metrics["total_scripts_generated"],
                "total_videos_created": self.system_metrics["total_videos_created"],
                "total_users": total_users,
                "average_response_time": self.system_metrics["average_response_time"],
                "error_rate": self.system_metrics["error_rate"],
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_human": str(uptime).split('.')[0]  # Remove microseconds
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {}
    
    async def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by activity"""
        try:
            user_scores = []
            
            for user_id, metrics in self.user_metrics.items():
                score = self._calculate_activity_score(user_id)
                user_scores.append({
                    "user_id": user_id,
                    "activity_score": score,
                    "scripts_generated": metrics.get("scripts_generated", 0),
                    "videos_created": metrics.get("videos_created", 0),
                    "api_calls": metrics.get("api_calls", 0),
                    "last_activity": metrics.get("last_activity")
                })
            
            # Sort by activity score
            user_scores.sort(key=lambda x: x["activity_score"], reverse=True)
            
            return user_scores[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top users: {str(e)}")
            return []
    
    async def export_analytics(self, user_id: str = None, format: str = "json") -> str:
        """Export analytics data"""
        try:
            if user_id:
                data = {
                    "user_id": user_id,
                    "dashboard_data": await self.get_dashboard_data(user_id),
                    "usage_data": await self.get_usage_data(user_id),
                    "exported_at": datetime.utcnow().isoformat()
                }
            else:
                data = {
                    "system_stats": await self._get_system_stats(),
                    "top_users": await self.get_top_users(),
                    "exported_at": datetime.utcnow().isoformat()
                }
            
            if format == "json":
                return json.dumps(data, indent=2)
            else:
                # Could implement CSV or other formats
                return json.dumps(data, indent=2)
                
        except Exception as e:
            logger.error(f"Error exporting analytics: {str(e)}")
            return "{}"
