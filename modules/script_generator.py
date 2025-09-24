"""
AI Content Studio - Script Generator Module
Handles AI-powered script generation with multiple providers
"""

import asyncio
import json
import logging
import hashlib
import random
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
import openai
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class ScriptGenerator:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.anthropic_client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.script_templates = self._load_templates()
        self.cost_tracker = {}
        
    def _load_templates(self) -> Dict[str, Any]:
        """Load script templates"""
        return {
            "professional": {
                "hook": "Let's explore {topic} and discover how it can transform your approach.",
                "structure": ["hook", "main_points", "call_to_action"],
                "tone": "professional and informative"
            },
            "casual": {
                "hook": "Hey there! Today we're diving into {topic} - and trust me, you'll want to stick around for this.",
                "structure": ["hook", "personal_story", "main_points", "call_to_action"],
                "tone": "friendly and conversational"
            },
            "educational": {
                "hook": "Understanding {topic} is crucial for success. Let me break it down for you.",
                "structure": ["hook", "definition", "examples", "practical_tips", "call_to_action"],
                "tone": "educational and clear"
            },
            "entertaining": {
                "hook": "Buckle up! We're about to explore {topic} in a way you've never seen before.",
                "structure": ["hook", "story", "humor", "main_points", "call_to_action"],
                "tone": "entertaining and engaging"
            }
        }
    
    async def generate_script(
        self,
        topic: str,
        duration: int = 30,
        style: str = "professional",
        user_id: str = None
    ) -> Dict[str, Any]:
        """Generate AI-powered script"""
        try:
            # Validate inputs
            if not topic or len(topic.strip()) < 3:
                raise ValueError("Topic must be at least 3 characters long")
            
            if duration < 10 or duration > 300:
                raise ValueError("Duration must be between 10 and 300 seconds")
            
            if style not in self.script_templates:
                style = "professional"
            
            # Generate script ID
            script_id = self._generate_script_id(topic, user_id)
            
            # Check if script already exists
            existing_script = await self._get_existing_script(script_id)
            if existing_script:
                return existing_script
            
            # Generate script content
            script_content = await self._generate_content(
                topic, duration, style, user_id
            )
            
            # Calculate metrics
            word_count = len(script_content.split())
            estimated_duration = self._calculate_duration(script_content)
            
            # Create script object
            script = {
                "script_id": script_id,
                "topic": topic,
                "content": script_content,
                "style": style,
                "duration": duration,
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "provider": "ensemble_ai",
                "cost": self._calculate_cost(word_count),
                "quality_score": self._calculate_quality_score(script_content)
            }
            
            # Save script
            await self._save_script(script)
            
            # Update cost tracking
            self._update_cost_tracking(user_id, script["cost"])
            
            logger.info(f"Generated script {script_id} for user {user_id}")
            return script
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise
    
    async def _generate_content(
        self,
        topic: str,
        duration: int,
        style: str,
        user_id: str
    ) -> str:
        """Generate script content using AI"""
        try:
            # Get template
            template = self.script_templates[style]
            
            # Create prompt
            prompt = self._create_prompt(topic, duration, style, template)
            
            # Try multiple providers for better results
            providers = ["openai", "anthropic"]
            content = None
            
            for provider in providers:
                try:
                    if provider == "openai":
                        content = await self._generate_with_openai(prompt)
                    elif provider == "anthropic":
                        content = await self._generate_with_anthropic(prompt)
                    
                    if content and len(content.strip()) > 50:
                        break
                        
                except Exception as e:
                    logger.warning(f"Provider {provider} failed: {str(e)}")
                    continue
            
            # Fallback to template-based generation
            if not content:
                content = self._generate_with_template(topic, duration, style, template)
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
    
    def _create_prompt(self, topic: str, duration: int, style: str, template: Dict) -> str:
        """Create AI prompt for script generation"""
        return f"""
        Create a {duration}-second video script about "{topic}" in a {template['tone']} style.
        
        Structure:
        - Hook (0-5 seconds): Grab attention immediately
        - Main Content (5-{duration-5} seconds): Deliver value with clear points
        - Call to Action (last 5 seconds): Encourage engagement
        
        Style: {style}
        Tone: {template['tone']}
        
        Requirements:
        - Keep it engaging and conversational
        - Include specific, actionable points
        - End with a strong call to action
        - Aim for approximately {duration * 2} words
        - Make it suitable for social media
        
        Format the response as a complete script with clear sections.
        """
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate content using OpenAI"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert video script writer specializing in engaging, viral content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise
    
    async def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate content using Anthropic"""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}")
            raise
    
    def _generate_with_template(self, topic: str, duration: int, style: str, template: Dict) -> str:
        """Generate content using template fallback"""
        hook = template["hook"].format(topic=topic)
        
        # Generate main points based on topic
        main_points = self._generate_main_points(topic, duration)
        
        call_to_action = self._generate_call_to_action(style)
        
        return f"""
        # {topic}

        ## Hook (0-5 seconds)
        {hook}

        ## Main Content (5-{duration-5} seconds)
        {main_points}

        ## Call to Action ({duration-5}-{duration} seconds)
        {call_to_action}

        ---
        **Word Count**: {len(main_points.split()) + len(hook.split()) + len(call_to_action.split())} words
        **Estimated Duration**: {duration} seconds
        **Style**: {style}
        **Tone**: {template['tone']}
        **Generated with AI Content Studio Template Engine**
        """
    
    def _generate_main_points(self, topic: str, duration: int) -> str:
        """Generate main content points"""
        points = [
            f"Understanding {topic} is more important than you might think.",
            f"Here are three key insights about {topic}:",
            f"1. **First Point**: This is where the magic happens with {topic}.",
            f"2. **Second Point**: The impact is real and measurable.",
            f"3. **Third Point**: This isn't just theory - it's practical advice you can use today."
        ]
        return "\n\n".join(points)
    
    def _generate_call_to_action(self, style: str) -> str:
        """Generate call to action based on style"""
        ctas = {
            "professional": "What are your thoughts on this? Share your experience in the comments below, and don't forget to follow for more insights like this.",
            "casual": "So what do you think? Drop a comment and let me know! Hit that follow button for more content like this.",
            "educational": "I'd love to hear your thoughts! Comment below with your questions, and subscribe for more educational content.",
            "entertaining": "That was fun! What's your take? Comment below, follow for more entertainment, and I'll see you in the next video!"
        }
        return ctas.get(style, ctas["professional"])
    
    def _generate_script_id(self, topic: str, user_id: str = None) -> str:
        """Generate unique script ID"""
        content = f"{topic}_{user_id}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _calculate_duration(self, content: str) -> int:
        """Calculate estimated duration from content"""
        word_count = len(content.split())
        # Average speaking rate: 150 words per minute
        return max(10, int(word_count / 2.5))
    
    def _calculate_cost(self, word_count: int) -> float:
        """Calculate generation cost"""
        # Base cost: $0.01 per 100 words
        return round((word_count / 100) * 0.01, 4)
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate content quality score"""
        # Simple quality metrics
        word_count = len(content.split())
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        
        if sentence_count == 0:
            return 0.5
        
        avg_sentence_length = word_count / sentence_count
        
        # Quality score based on sentence length and content structure
        if 10 <= avg_sentence_length <= 20:
            return min(1.0, 0.7 + (word_count / 1000) * 0.3)
        else:
            return max(0.3, 0.7 - abs(avg_sentence_length - 15) * 0.02)
    
    def _update_cost_tracking(self, user_id: str, cost: float):
        """Update cost tracking for user"""
        if user_id not in self.cost_tracker:
            self.cost_tracker[user_id] = 0.0
        self.cost_tracker[user_id] += cost
    
    async def _get_existing_script(self, script_id: str) -> Optional[Dict]:
        """Check if script already exists"""
        # In a real implementation, this would query the database
        return None
    
    async def _save_script(self, script: Dict):
        """Save script to database"""
        # In a real implementation, this would save to database
        logger.info(f"Saving script {script['script_id']}")
    
    async def get_script(self, script_id: str, user_id: str) -> Optional[Dict]:
        """Get script by ID"""
        try:
            # In a real implementation, this would query the database
            # For now, return a mock script
            return {
                "script_id": script_id,
                "topic": "Sample Topic",
                "content": "Sample script content...",
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting script: {str(e)}")
            return None
    
    async def get_user_scripts(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's scripts"""
        try:
            # In a real implementation, this would query the database
            return []
        except Exception as e:
            logger.error(f"Error getting user scripts: {str(e)}")
            return []
    
    def get_cost_summary(self, user_id: str) -> Dict:
        """Get cost summary for user"""
        total_cost = self.cost_tracker.get(user_id, 0.0)
        return {
            "user_id": user_id,
            "total_cost": total_cost,
            "script_count": len([k for k in self.cost_tracker.keys() if k == user_id]),
            "average_cost_per_script": total_cost / max(1, len([k for k in self.cost_tracker.keys() if k == user_id]))
        }
