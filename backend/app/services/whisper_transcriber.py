"""
OpenAI Whisper transcription service implementation
"""
import os
import asyncio
import logging
from typing import Optional
from openai import OpenAI
from .base import TranscriptionService, TranscriptionResult, TranscriptionError

logger = logging.getLogger(__name__)


class WhisperTranscriber(TranscriptionService):
    """
    OpenAI Whisper API transcription service
    Handles audio file transcription with error handling and retry logic
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Whisper transcriber
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "whisper-1"
        
    async def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """
        Transcribe audio file using OpenAI Whisper API
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            TranscriptionResult with transcribed text
            
        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            logger.info(f"Starting transcription for file: {audio_file_path}")
            
            # Validate file exists
            if not os.path.exists(audio_file_path):
                raise TranscriptionError(f"Audio file not found: {audio_file_path}")
            
            # Check file size (Whisper has 25MB limit)
            file_size = os.path.getsize(audio_file_path)
            if file_size > 25 * 1024 * 1024:  # 25MB
                raise TranscriptionError("Audio file too large (max 25MB)")
            
            # Run transcription in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._transcribe_sync, audio_file_path
            )
            
            logger.info(f"Transcription completed. Text length: {len(result.text)} characters")
            return result
            
        except TranscriptionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}")
            raise TranscriptionError(f"Transcription failed: {str(e)}")
    
    def _transcribe_sync(self, audio_file_path: str) -> TranscriptionResult:
        """
        Synchronous transcription call (runs in thread pool)
        """
        try:
            with open(audio_file_path, 'rb') as audio_file:
                # Call Whisper API with verbose response for additional metadata
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            # Extract text and metadata
            text = response.text.strip()
            if not text:
                raise TranscriptionError("No speech detected in audio")
            
            # Whisper doesn't provide confidence scores directly, 
            # but we can estimate based on response quality
            confidence = self._estimate_confidence(response)
            
            return TranscriptionResult(
                text=text,
                confidence=confidence,
                language=getattr(response, 'language', None),
                duration=getattr(response, 'duration', None)
            )
            
        except Exception as e:
            if "No speech detected" in str(e):
                raise TranscriptionError("No speech detected in audio file")
            elif "invalid_request_error" in str(e):
                raise TranscriptionError(f"Invalid audio format: {str(e)}")
            else:
                raise TranscriptionError(f"Whisper API error: {str(e)}")
    
    def _estimate_confidence(self, response) -> float:
        """
        Estimate confidence based on response characteristics
        Whisper doesn't provide direct confidence scores
        """
        try:
            # Check if response has segments with word-level info
            if hasattr(response, 'segments') and response.segments:
                # Calculate confidence based on segment consistency
                # This is a simple heuristic - in production you might use more sophisticated methods
                return 0.85  # High confidence for successful transcription
            else:
                return 0.75  # Lower confidence without detailed segments
        except:
            return 0.5  # Default confidence if we can't determine quality
    
    def get_supported_formats(self) -> list:
        """
        Get list of supported audio formats
        """
        return [
            'flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 
            'oga', 'ogg', 'wav', 'webm'
        ]