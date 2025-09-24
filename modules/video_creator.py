"""
AI Content Studio - Video Creator Module
Handles AI-powered video creation and processing
"""

import asyncio
import json
import logging
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
import aiofiles

logger = logging.getLogger(__name__)

class VideoCreator:
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.video_templates = self._load_video_templates()
        self.voice_profiles = self._load_voice_profiles()
        self.cost_tracker = {}
        
    def _load_video_templates(self) -> Dict[str, Any]:
        """Load video templates"""
        return {
            "professional": {
                "style": "clean and corporate",
                "colors": ["#1e40af", "#3b82f6", "#60a5fa"],
                "fonts": ["Inter", "Roboto", "Open Sans"],
                "transitions": "smooth",
                "background": "gradient"
            },
            "casual": {
                "style": "friendly and approachable",
                "colors": ["#f59e0b", "#fbbf24", "#fcd34d"],
                "fonts": ["Poppins", "Nunito", "Lato"],
                "transitions": "bounce",
                "background": "pattern"
            },
            "educational": {
                "style": "clear and informative",
                "colors": ["#059669", "#10b981", "#34d399"],
                "fonts": ["Source Sans Pro", "Merriweather", "Lora"],
                "transitions": "fade",
                "background": "minimal"
            },
            "entertaining": {
                "style": "dynamic and engaging",
                "colors": ["#dc2626", "#ef4444", "#f87171"],
                "fonts": ["Montserrat", "Bebas Neue", "Oswald"],
                "transitions": "zoom",
                "background": "animated"
            }
        }
    
    def _load_voice_profiles(self) -> Dict[str, Any]:
        """Load voice profiles"""
        return {
            "professional_male": {
                "voice_id": "pNInz6obpgDQGcFmaJgB",
                "name": "Professional Male",
                "description": "Clear, authoritative voice perfect for business content",
                "language": "en-US",
                "accent": "American"
            },
            "professional_female": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Professional Female",
                "description": "Warm, professional voice ideal for educational content",
                "language": "en-US",
                "accent": "American"
            },
            "casual_male": {
                "voice_id": "VR6AewLTigWG4xSOukaG",
                "name": "Casual Male",
                "description": "Friendly, conversational voice for casual content",
                "language": "en-US",
                "accent": "American"
            },
            "casual_female": {
                "voice_id": "AZnzlk1XvdvUeBnXmlld",
                "name": "Casual Female",
                "description": "Energetic, engaging voice for entertainment content",
                "language": "en-US",
                "accent": "American"
            }
        }
    
    async def create_video(
        self,
        script_id: str,
        style: str = "professional",
        voice_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Create video from script"""
        try:
            # Validate inputs
            if not script_id:
                raise ValueError("Script ID is required")
            
            if style not in self.video_templates:
                style = "professional"
            
            # Generate video ID
            video_id = self._generate_video_id(script_id, user_id)
            
            # Check if video already exists
            existing_video = await self._get_existing_video(video_id)
            if existing_video:
                return existing_video
            
            # Get script content
            script_content = await self._get_script_content(script_id)
            if not script_content:
                raise ValueError("Script not found")
            
            # Create video components
            video_components = await self._create_video_components(
                script_content, style, voice_id
            )
            
            # Generate video
            video_url = await self._generate_video(video_components)
            
            # Create video object
            video = {
                "video_id": video_id,
                "script_id": script_id,
                "style": style,
                "voice_id": voice_id,
                "user_id": user_id,
                "video_url": video_url,
                "thumbnail_url": await self._generate_thumbnail(video_components),
                "duration": video_components["duration"],
                "resolution": "1920x1080",
                "format": "mp4",
                "file_size": await self._get_file_size(video_url),
                "created_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "cost": self._calculate_cost(video_components),
                "quality_score": self._calculate_quality_score(video_components)
            }
            
            # Save video
            await self._save_video(video)
            
            # Update cost tracking
            self._update_cost_tracking(user_id, video["cost"])
            
            logger.info(f"Created video {video_id} for user {user_id}")
            return video
            
        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            raise
    
    async def _create_video_components(
        self,
        script_content: str,
        style: str,
        voice_id: str = None
    ) -> Dict[str, Any]:
        """Create video components"""
        try:
            # Get template
            template = self.video_templates[style]
            
            # Select voice
            if not voice_id:
                voice_id = self._select_voice_for_style(style)
            
            voice_profile = self.voice_profiles.get(voice_id, self.voice_profiles["professional_male"])
            
            # Generate audio
            audio_url = await self._generate_audio(script_content, voice_profile)
            
            # Generate visuals
            visuals = await self._generate_visuals(script_content, template)
            
            # Calculate duration
            duration = self._calculate_video_duration(script_content)
            
            return {
                "script_content": script_content,
                "style": style,
                "template": template,
                "voice_profile": voice_profile,
                "audio_url": audio_url,
                "visuals": visuals,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Error creating video components: {str(e)}")
            raise
    
    async def _generate_audio(self, script_content: str, voice_profile: Dict) -> str:
        """Generate audio using ElevenLabs"""
        try:
            if not self.elevenlabs_api_key:
                # Fallback to mock audio generation
                return await self._generate_mock_audio(script_content)
            
            url = "https://api.elevenlabs.io/v1/text-to-speech"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": script_content,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{url}/{voice_profile['voice_id']}",
                    json=data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        # Save audio file and return URL
                        audio_url = await self._save_audio_file(audio_data)
                        return audio_url
                    else:
                        raise Exception(f"ElevenLabs API error: {response.status}")
                        
        except Exception as e:
            logger.warning(f"ElevenLabs generation failed: {str(e)}")
            return await self._generate_mock_audio(script_content)
    
    async def _generate_mock_audio(self, script_content: str) -> str:
        """Generate mock audio URL"""
        # In a real implementation, this would generate actual audio
        return f"https://mock-audio-url.com/audio_{hashlib.md5(script_content.encode()).hexdigest()[:8]}.mp3"
    
    async def _generate_visuals(self, script_content: str, template: Dict) -> List[Dict]:
        """Generate visual components"""
        try:
            # Parse script into segments
            segments = self._parse_script_segments(script_content)
            
            visuals = []
            for i, segment in enumerate(segments):
                visual = {
                    "segment_id": i,
                    "text": segment["text"],
                    "duration": segment["duration"],
                    "style": template["style"],
                    "colors": template["colors"],
                    "font": template["fonts"][0],
                    "background": template["background"],
                    "animation": self._get_animation_for_segment(segment, template)
                }
                visuals.append(visual)
            
            return visuals
            
        except Exception as e:
            logger.error(f"Error generating visuals: {str(e)}")
            return []
    
    def _parse_script_segments(self, script_content: str) -> List[Dict]:
        """Parse script into visual segments"""
        # Simple parsing - in reality, this would be more sophisticated
        lines = script_content.split('\n')
        segments = []
        
        current_segment = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                current_segment += line + " "
                if len(current_segment) > 100:  # Split at reasonable length
                    segments.append({
                        "text": current_segment.strip(),
                        "duration": max(3, len(current_segment.split()) / 3)  # ~3 words per second
                    })
                    current_segment = ""
        
        if current_segment:
            segments.append({
                "text": current_segment.strip(),
                "duration": max(3, len(current_segment.split()) / 3)
            })
        
        return segments
    
    def _get_animation_for_segment(self, segment: Dict, template: Dict) -> str:
        """Get animation type for segment"""
        animations = {
            "smooth": ["fadeIn", "slideIn", "zoomIn"],
            "bounce": ["bounceIn", "pulse", "shake"],
            "fade": ["fadeIn", "fadeOut"],
            "zoom": ["zoomIn", "zoomOut", "rotate"]
        }
        
        available_animations = animations.get(template["transitions"], animations["smooth"])
        return available_animations[len(segment["text"]) % len(available_animations)]
    
    async def _generate_video(self, components: Dict) -> str:
        """Generate final video"""
        try:
            # In a real implementation, this would use FFmpeg or similar
            # to combine audio and visuals into a video
            
            video_id = hashlib.md5(
                f"{components['script_content']}_{components['style']}".encode()
            ).hexdigest()[:12]
            
            # Mock video generation
            video_url = f"https://mock-video-url.com/video_{video_id}.mp4"
            
            logger.info(f"Generated video: {video_url}")
            return video_url
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
    async def _generate_thumbnail(self, components: Dict) -> str:
        """Generate video thumbnail"""
        try:
            # In a real implementation, this would generate an actual thumbnail
            thumbnail_id = hashlib.md5(
                f"{components['script_content'][:50]}_{components['style']}".encode()
            ).hexdigest()[:8]
            
            return f"https://mock-thumbnail-url.com/thumb_{thumbnail_id}.jpg"
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return ""
    
    async def _get_file_size(self, video_url: str) -> int:
        """Get video file size"""
        # Mock file size calculation
        return random.randint(5000000, 50000000)  # 5-50 MB
    
    def _calculate_video_duration(self, script_content: str) -> int:
        """Calculate video duration from script"""
        word_count = len(script_content.split())
        # Average speaking rate: 150 words per minute
        return max(10, int(word_count / 2.5))
    
    def _calculate_cost(self, components: Dict) -> float:
        """Calculate video creation cost"""
        # Base cost calculation
        duration = components["duration"]
        base_cost = 0.05  # $0.05 per second
        return round(duration * base_cost, 4)
    
    def _calculate_quality_score(self, components: Dict) -> float:
        """Calculate video quality score"""
        # Quality based on duration, style complexity, and content
        duration_score = min(1.0, components["duration"] / 60)  # Longer videos score higher
        style_score = 0.8  # All styles are good
        content_score = min(1.0, len(components["script_content"]) / 1000)  # More content = better
        
        return round((duration_score + style_score + content_score) / 3, 2)
    
    def _select_voice_for_style(self, style: str) -> str:
        """Select appropriate voice for style"""
        voice_mapping = {
            "professional": "professional_male",
            "casual": "casual_female",
            "educational": "professional_female",
            "entertaining": "casual_male"
        }
        return voice_mapping.get(style, "professional_male")
    
    def _update_cost_tracking(self, user_id: str, cost: float):
        """Update cost tracking for user"""
        if user_id not in self.cost_tracker:
            self.cost_tracker[user_id] = 0.0
        self.cost_tracker[user_id] += cost
    
    async def _get_script_content(self, script_id: str) -> Optional[str]:
        """Get script content by ID"""
        # In a real implementation, this would query the database
        return "Sample script content for video creation..."
    
    async def _get_existing_video(self, video_id: str) -> Optional[Dict]:
        """Check if video already exists"""
        # In a real implementation, this would query the database
        return None
    
    async def _save_video(self, video: Dict):
        """Save video to database"""
        # In a real implementation, this would save to database
        logger.info(f"Saving video {video['video_id']}")
    
    async def _save_audio_file(self, audio_data: bytes) -> str:
        """Save audio file and return URL"""
        # In a real implementation, this would save to file storage
        audio_id = hashlib.md5(audio_data).hexdigest()[:8]
        return f"https://mock-audio-storage.com/audio_{audio_id}.mp3"
    
    async def get_video(self, video_id: str, user_id: str) -> Optional[Dict]:
        """Get video by ID"""
        try:
            # In a real implementation, this would query the database
            return {
                "video_id": video_id,
                "user_id": user_id,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting video: {str(e)}")
            return None
    
    async def get_user_videos(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's videos"""
        try:
            # In a real implementation, this would query the database
            return []
        except Exception as e:
            logger.error(f"Error getting user videos: {str(e)}")
            return []
    
    def get_cost_summary(self, user_id: str) -> Dict:
        """Get cost summary for user"""
        total_cost = self.cost_tracker.get(user_id, 0.0)
        return {
            "user_id": user_id,
            "total_cost": total_cost,
            "video_count": len([k for k in self.cost_tracker.keys() if k == user_id]),
            "average_cost_per_video": total_cost / max(1, len([k for k in self.cost_tracker.keys() if k == user_id]))
        }
