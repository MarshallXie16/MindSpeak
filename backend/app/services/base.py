"""
Base interfaces for AI services
Following the Interface Segregation Principle and Dependency Inversion Principle
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result of audio transcription"""
    text: str
    confidence: float
    language: Optional[str] = None
    duration: Optional[float] = None


@dataclass
class EmotionAnalysis:
    """Emotion detection result"""
    name: str
    confidence: float


@dataclass
class JournalAnalysis:
    """Complete journal analysis result"""
    title: str
    formatted_content: str
    mood_score: int  # 1-10 scale
    emotions: List[EmotionAnalysis]
    insights: List[str]


class TranscriptionService(ABC):
    """
    Abstract base class for audio transcription services
    Allows easy swapping of transcription providers (Whisper, Azure, etc.)
    """
    
    @abstractmethod
    async def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            TranscriptionResult with text and metadata
            
        Raises:
            TranscriptionError: If transcription fails
        """
        pass


class JournalProcessor(ABC):
    """
    Abstract base class for journal processing services
    Allows easy swapping of AI providers (Claude, GPT, etc.)
    """
    
    @abstractmethod
    async def process_transcript(
        self, 
        transcript: str, 
        user_context: Optional[Dict[str, Any]] = None
    ) -> JournalAnalysis:
        """
        Process raw transcript into structured journal entry
        
        Args:
            transcript: Raw transcribed text
            user_context: User preferences, goals, custom instructions
            
        Returns:
            JournalAnalysis with formatted content and insights
            
        Raises:
            ProcessingError: If processing fails
        """
        pass


class AIServiceError(Exception):
    """Base exception for AI service errors"""
    pass


class TranscriptionError(AIServiceError):
    """Exception raised when transcription fails"""
    pass


class ProcessingError(AIServiceError):
    """Exception raised when journal processing fails"""
    pass