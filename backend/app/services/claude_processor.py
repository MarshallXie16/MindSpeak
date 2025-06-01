"""
Claude AI journal processing service implementation
"""
import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from .base import JournalProcessor, JournalAnalysis, EmotionAnalysis, ProcessingError

logger = logging.getLogger(__name__)


class ClaudeProcessor(JournalProcessor):
    """
    Claude AI service for processing journal transcripts
    Handles content restructuring, mood analysis, and insight generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude processor
        
        Args:
            api_key: Anthropic API key. If None, will use ANTHROPIC_API_KEY env var
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest model
        self.max_tokens = 4000
        
    async def process_transcript(
        self, 
        transcript: str, 
        user_context: Optional[Dict[str, Any]] = None
    ) -> JournalAnalysis:
        """
        Process transcript into structured journal entry using Claude
        
        Args:
            transcript: Raw transcribed text
            user_context: User preferences, goals, custom instructions
            
        Returns:
            JournalAnalysis with structured content and insights
        """
        try:
            logger.info(f"Starting Claude processing for transcript length: {len(transcript)}")
            
            if not transcript.strip():
                raise ProcessingError("Empty transcript provided")
            
            # Build context-aware prompt
            prompt = self._build_processing_prompt(transcript, user_context or {})
            
            # Run Claude API call in thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._process_sync, prompt
            )
            
            logger.info("Claude processing completed successfully")
            return result
            
        except ProcessingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Claude processing: {str(e)}")
            raise ProcessingError(f"Processing failed: {str(e)}")
    
    def _process_sync(self, prompt: str) -> JournalAnalysis:
        """
        Synchronous Claude API call (runs in thread pool)
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract and parse the response
            content = response.content[0].text
            return self._parse_claude_response(content)
            
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise ProcessingError(f"Claude API error: {str(e)}")
    
    def _build_processing_prompt(self, transcript: str, user_context: Dict[str, Any]) -> str:
        """
        Build comprehensive prompt for Claude based on transcript and user context
        """
        # Extract user context
        custom_instructions = user_context.get('custom_ai_instructions', '')
        goals = user_context.get('goals', [])
        
        # Format goals for prompt
        goals_text = ""
        if goals:
            goals_list = [goal.get('text', '') for goal in goals if goal.get('text')]
            if goals_list:
                goals_text = f"\nUser's Personal Goals:\n" + "\n".join(f"- {goal}" for goal in goals_list)
        
        # Build the main prompt
        prompt = f"""Transform this voice journal transcript into a structured, insightful journal entry.

VOICE TRANSCRIPT:
{transcript}

CONTEXT:
This is a personal voice journal entry. The user spoke naturally and may have:
- Used filler words (um, uh, like)
- Had incomplete thoughts or tangents
- Mentioned various topics spontaneously

YOUR TASK:
Create a well-structured journal entry that:

1. **PRESERVES THE USER'S AUTHENTIC VOICE** - Keep their personality and emotional tone
2. **ORGANIZES THOUGHTS LOGICALLY** - Group related ideas together
3. **FIXES GRAMMAR & FLOW** - Make it readable while keeping it natural
4. **MAINTAINS EMOTIONAL AUTHENTICITY** - Don't sanitize or over-optimize emotions

{goals_text}

{f"CUSTOM INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

OUTPUT FORMAT (JSON):
{{
    "title": "Engaging title that captures the essence (max 50 chars)",
    "formatted_content": "Well-structured journal entry maintaining user's voice and emotions",
    "mood_score": 7,
    "emotions": [
        {{"name": "hopeful", "confidence": 0.8}},
        {{"name": "anxious", "confidence": 0.6}},
        {{"name": "determined", "confidence": 0.5}}
    ],
    "insights": [
        "Specific observation about patterns or behaviors",
        "Actionable suggestion based on what they shared"
    ]
}}

GUIDELINES:
- Title: Capture the main theme/feeling, not just "Journal Entry"
- Content: 2-4 paragraphs, natural flow, maintain user's speaking style
- Mood: 1 (very negative) to 10 (very positive), be nuanced
- Emotions: Top 3 emotions with realistic confidence scores (0-1)
- Insights: 2-3 observations that are helpful but not preachy

Generate the JSON response now:"""

        return prompt
    
    def _parse_claude_response(self, response_text: str) -> JournalAnalysis:
        """
        Parse Claude's JSON response into JournalAnalysis object
        """
        try:
            # Extract JSON from response (Claude sometimes adds explanation text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ProcessingError("No valid JSON found in Claude response")
            
            json_text = response_text[json_start:json_end]
            
            # Clean the JSON text to handle control characters and encoding issues
            json_text = self._clean_json_text(json_text)
            
            data = json.loads(json_text)
            
            # Validate required fields
            required_fields = ['title', 'formatted_content', 'mood_score', 'emotions', 'insights']
            for field in required_fields:
                if field not in data:
                    raise ProcessingError(f"Missing required field in response: {field}")
            
            # Parse emotions
            emotions = []
            for emotion_data in data.get('emotions', []):
                if isinstance(emotion_data, dict) and 'name' in emotion_data and 'confidence' in emotion_data:
                    emotions.append(EmotionAnalysis(
                        name=emotion_data['name'],
                        confidence=float(emotion_data['confidence'])
                    ))
            
            # Validate mood score
            mood_score = int(data['mood_score'])
            if not 1 <= mood_score <= 10:
                mood_score = max(1, min(10, mood_score))  # Clamp to valid range
            
            # Ensure insights is a list
            insights = data.get('insights', [])
            if isinstance(insights, str):
                insights = [insights]
            
            return JournalAnalysis(
                title=data['title'][:50],  # Enforce title length limit
                formatted_content=data['formatted_content'],
                mood_score=mood_score,
                emotions=emotions,
                insights=insights
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude JSON response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            logger.error(f"Cleaned JSON text: {json_text}")
            
            # Try alternative JSON parsing approaches
            try:
                # Try with ast.literal_eval for simple cases (not recommended for production)
                import ast
                data = ast.literal_eval(json_text)
                logger.info("Successfully parsed with ast.literal_eval as fallback")
            except Exception as fallback_error:
                # Try extracting data manually as last resort
                logger.error(f"ast.literal_eval also failed: {str(fallback_error)}")
                logger.error("All JSON parsing methods failed, attempting manual extraction")
                data = self._extract_data_manually(response_text)
                if not data:
                    # Final fallback - create a minimal valid structure
                    logger.error("Manual extraction failed, using fallback structure")
                    data = {
                        'title': 'Processing Completed',
                        'formatted_content': 'Entry was processed but formatting failed. Please check the original transcript.',
                        'mood_score': 5,
                        'emotions': [],
                        'insights': ['Processing completed with errors - please review manually']
                    }
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Invalid response structure from Claude: {str(e)}")
            raise ProcessingError("Invalid response structure from Claude")
    
    def _clean_json_text(self, json_text: str) -> str:
        """
        Clean JSON text to handle control characters and encoding issues
        """
        import re
        
        # Remove or replace common problematic control characters
        # Keep newlines and tabs as they're valid in JSON strings
        json_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_text)
        
        # Ensure proper UTF-8 encoding
        if isinstance(json_text, str):
            json_text = json_text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Handle unescaped newlines within JSON string values
        # This is specifically for Claude responses with Chinese text that may contain literal newlines
        try:
            # Find formatted_content field and escape any unescaped newlines within it
            content_pattern = r'("formatted_content":\s*")(.*?)("(?=,\s*"\w+":))'
            
            def escape_newlines_in_content(match):
                prefix = match.group(1)
                content = match.group(2)
                suffix = match.group(3)
                
                # Escape unescaped newlines in the content
                # Only escape if they're not already escaped
                content = re.sub(r'(?<!\\)\n', '\\\\n', content)
                content = re.sub(r'(?<!\\)"', '\\\\"', content)
                
                return prefix + content + suffix
            
            json_text = re.sub(content_pattern, escape_newlines_in_content, json_text, flags=re.DOTALL)
            
        except Exception as e:
            logger.warning(f"Could not clean newlines in JSON: {e}")
        
        return json_text
    
    def _extract_data_manually(self, response_text: str) -> Dict[str, Any]:
        """
        Manual extraction as last resort when JSON parsing fails
        """
        try:
            import re
            
            logger.info("Attempting manual extraction from response")
            
            # Extract title - handle both ASCII and Unicode content
            title_match = re.search(r'"title":\s*"([^"]*)"', response_text, re.UNICODE)
            title = title_match.group(1) if title_match else "Untitled Entry"
            
            # Extract formatted_content - improved approach for multiline Chinese text
            try:
                # Find the formatted_content section using a more robust pattern
                content_pattern = r'"formatted_content":\s*"(.*?)"(?=,\s*"\w+":)'
                content_match = re.search(content_pattern, response_text, re.DOTALL | re.UNICODE)
                
                if content_match:
                    content = content_match.group(1)
                    # Clean up escaped characters and newlines in the content
                    content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                else:
                    # Fallback: try to find content between formatted_content and mood_score
                    content_start_marker = '"formatted_content": "'
                    content_start = response_text.find(content_start_marker)
                    if content_start != -1:
                        content_start += len(content_start_marker)
                        
                        # Look for the end pattern more flexibly
                        possible_ends = [
                            '",\n    "mood_score"',
                            '",\n        "mood_score"', 
                            '",\n"mood_score"',
                            '",\n\t"mood_score"',
                            '",'
                        ]
                        
                        content_end = -1
                        for end_pattern in possible_ends:
                            content_end = response_text.find(end_pattern, content_start)
                            if content_end != -1:
                                break
                        
                        if content_end != -1:
                            content = response_text[content_start:content_end]
                            # Clean up the content
                            content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                        else:
                            content = "Could not extract content properly"
                    else:
                        content = "Content start marker not found"
                        
            except Exception as e:
                logger.error(f"Content extraction failed: {e}")
                content = "Content extraction failed"
            
            # Extract mood_score
            mood_match = re.search(r'"mood_score":\s*(\d+)', response_text)
            mood_score = int(mood_match.group(1)) if mood_match else 5
            
            # Try to extract emotions array
            emotions = []
            try:
                emotions_section = re.search(r'"emotions":\s*\[(.*?)\]', response_text, re.DOTALL)
                if emotions_section:
                    # Simple extraction - just get names if possible
                    emotion_names = re.findall(r'"name":\s*"([^"]*)"', emotions_section.group(1))
                    emotions = [{"name": name, "confidence": 0.5} for name in emotion_names[:3]]
            except:
                pass
            
            # Try to extract insights array
            insights = []
            try:
                insights_section = re.search(r'"insights":\s*\[(.*?)\]', response_text, re.DOTALL)
                if insights_section:
                    insight_texts = re.findall(r'"([^"]*)"', insights_section.group(1))
                    insights = insight_texts[:3] if insight_texts else ["Manual extraction completed"]
            except:
                insights = ["Processing completed with manual extraction"]
            
            result = {
                'title': title,
                'formatted_content': content,
                'mood_score': mood_score,
                'emotions': emotions,
                'insights': insights
            }
            
            logger.info(f"Manual extraction successful: {result['title']}")
            return result
            
        except Exception as e:
            logger.error(f"Manual extraction failed: {str(e)}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Claude model
        """
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "provider": "Anthropic"
        }