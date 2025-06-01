"""
Journal AI Service - Orchestrates the complete AI processing pipeline
"""
import os
import logging
from typing import Dict, Any, Optional, Generator
from dataclasses import asdict

from .base import TranscriptionService, JournalProcessor, AIServiceError
from .whisper_transcriber import WhisperTranscriber
from .claude_processor import ClaudeProcessor

logger = logging.getLogger(__name__)


class JournalAIService:
    """
    Main service class that orchestrates the AI processing pipeline
    Follows the Facade pattern to provide a simple interface to complex subsystems
    """
    
    def __init__(
        self, 
        transcriber: Optional[TranscriptionService] = None,
        processor: Optional[JournalProcessor] = None
    ):
        """
        Initialize AI service with configurable components
        
        Args:
            transcriber: Audio transcription service (defaults to WhisperTranscriber)
            processor: Journal processing service (defaults to ClaudeProcessor)
        """
        self.transcriber = transcriber or WhisperTranscriber()
        self.processor = processor or ClaudeProcessor()
        
    async def process_audio_entry(
        self, 
        audio_file_path: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Complete AI processing pipeline for audio journal entries
        
        Yields progress updates during processing:
        - transcribing (25%)
        - restructuring (50%) 
        - analyzing (75%)
        - complete (100%)
        
        Args:
            audio_file_path: Path to the uploaded audio file
            user_context: User preferences, goals, and custom instructions
            
        Yields:
            Dict with status, progress, and results
            
        Raises:
            AIServiceError: If any step in the pipeline fails
        """
        try:
            logger.info(f"Starting AI processing pipeline for: {audio_file_path}")
            
            # Step 1: Transcription (0-25%)
            yield {
                'status': 'transcribing',
                'progress': 10,
                'message': 'Converting speech to text...'
            }
            
            transcription_result = await self.transcriber.transcribe(audio_file_path)
            
            yield {
                'status': 'transcribing',
                'progress': 25,
                'message': 'Transcription complete',
                'transcription': {
                    'text': transcription_result.text,
                    'confidence': transcription_result.confidence,
                    'language': transcription_result.language
                }
            }
            
            # Step 2: Journal Processing (25-75%)
            yield {
                'status': 'restructuring',
                'progress': 40,
                'message': 'Analyzing and restructuring content...'
            }
            
            analysis_result = await self.processor.process_transcript(
                transcription_result.text,
                user_context
            )
            
            yield {
                'status': 'analyzing',
                'progress': 75,
                'message': 'Generating insights and mood analysis...'
            }
            
            # Step 3: Complete (75-100%)
            yield {
                'status': 'complete',
                'progress': 100,
                'message': 'Processing complete!',
                'result': {
                    'raw_transcript': transcription_result.text,
                    'title': analysis_result.title,
                    'formatted_content': analysis_result.formatted_content,
                    'mood_score': analysis_result.mood_score,
                    'emotions': [asdict(emotion) for emotion in analysis_result.emotions],
                    'insights': analysis_result.insights,
                    'transcription_confidence': transcription_result.confidence
                }
            }
            
            logger.info("AI processing pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"AI processing pipeline failed: {str(e)}")
            yield {
                'status': 'error',
                'progress': 0,
                'message': f'Processing failed: {str(e)}',
                'error': str(e)
            }
    
    async def process_text_entry(
        self, 
        text_content: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process written text entry (skip transcription)
        
        Args:
            text_content: Raw text content
            user_context: User preferences and context
            
        Returns:
            Processed journal entry data
        """
        try:
            logger.info(f"Processing text entry of length: {len(text_content)}")
            
            analysis_result = await self.processor.process_transcript(
                text_content,
                user_context
            )
            
            return {
                'raw_transcript': text_content,
                'title': analysis_result.title,
                'formatted_content': analysis_result.formatted_content,
                'mood_score': analysis_result.mood_score,
                'emotions': [asdict(emotion) for emotion in analysis_result.emotions],
                'insights': analysis_result.insights
            }
            
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            raise AIServiceError(f"Text processing failed: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if all AI services are properly configured
        
        Returns:
            Dict with service status information
        """
        status = {
            'transcription_service': 'unknown',
            'processing_service': 'unknown',
            'overall_status': 'unknown'
        }
        
        try:
            # Check transcription service
            if hasattr(self.transcriber, 'api_key') and self.transcriber.api_key:
                status['transcription_service'] = 'configured'
            else:
                status['transcription_service'] = 'missing_api_key'
            
            # Check processing service  
            if hasattr(self.processor, 'api_key') and self.processor.api_key:
                status['processing_service'] = 'configured'
            else:
                status['processing_service'] = 'missing_api_key'
            
            # Overall status
            if (status['transcription_service'] == 'configured' and 
                status['processing_service'] == 'configured'):
                status['overall_status'] = 'ready'
            else:
                status['overall_status'] = 'configuration_error'
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            status['overall_status'] = 'error'
            status['error'] = str(e)
        
        return status


# Global service instance
_ai_service_instance = None


def get_ai_service() -> JournalAIService:
    """
    Get singleton instance of JournalAIService
    Implements singleton pattern for service reuse
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = JournalAIService()
    return _ai_service_instance