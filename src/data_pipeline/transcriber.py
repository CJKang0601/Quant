"""Speech-to-Text transcription using Whisper."""
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from src.utils.logger import get_logger
from src.utils.data_models import TranscriptionResult

logger = get_logger(__name__)


class WhisperTranscriber:
    """Transcribes audio using OpenAI Whisper."""
    
    def __init__(self, model_size: str = "base", device: str = "cpu"):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_size: Model size ('tiny', 'base', 'small', 'medium', 'large')
            device: Device to use ('cpu' or 'cuda')
        """
        try:
            import whisper
            self.whisper = whisper
            self.model = whisper.load_model(model_size, device=device)
            logger.info(f"Whisper model loaded: {model_size} on {device}")
        except ImportError:
            logger.error("openai-whisper not installed. Install with: pip install openai-whisper")
            raise
    
    def transcribe(self, audio_path: str, language: str = "zh") -> Optional[str]:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'zh' for Chinese, 'en' for English)
            
        Returns:
            Transcribed text, or None if failed
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False,
            )
            
            text = result.get('text', '')
            logger.info(f"Transcription completed. Length: {len(text)} characters")
            return text
        
        except Exception as e:
            logger.error(f"Error transcribing {audio_path}: {e}")
            return None
    
    def transcribe_to_result(
        self,
        audio_path: str,
        source_id: str,
        source_type: str = "youtube",
        source_title: str = "",
        source_url: Optional[str] = None,
        language: str = "zh",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe audio and return structured result.
        
        Args:
            audio_path: Path to audio file
            source_id: Unique identifier for source
            source_type: Type of source ('youtube' or 'podcast')
            source_title: Title of source content
            source_url: URL of source (optional)
            language: Language code
            metadata: Additional metadata dict
            
        Returns:
            TranscriptionResult or None if failed
        """
        try:
            text = self.transcribe(audio_path, language)
            if not text:
                return None
            
            # Get audio duration
            duration_seconds = self._get_audio_duration(audio_path)
            
            result = TranscriptionResult(
                source_id=source_id,
                source_type=source_type,
                source_title=source_title,
                source_url=source_url,
                transcript=text,
                duration_seconds=duration_seconds,
                language=language,
                processed_at=datetime.utcnow(),
                metadata=metadata or {},
            )
            
            logger.info(f"TranscriptionResult created for {source_id}")
            return result
        
        except Exception as e:
            logger.error(f"Error creating TranscriptionResult: {e}")
            return None
    
    def _get_audio_duration(self, audio_path: str) -> int:
        """
        Get audio duration in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            import librosa
            duration = librosa.get_duration(path=audio_path)
            return int(duration)
        except:
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(audio_path)
                return int(len(audio) / 1000)
            except:
                logger.warning(f"Could not determine duration for {audio_path}")
                return 0


class FasterWhisperTranscriber(WhisperTranscriber):
    """Faster Whisper implementation for better performance."""
    
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "default"):
        """
        Initialize Faster Whisper transcriber.
        
        Args:
            model_size: Model size
            device: Device to use
            compute_type: Compute type ('default', 'int8', 'float16')
        """
        try:
            from faster_whisper import WhisperModel
            self.faster_whisper = WhisperModel
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
            )
            logger.info(f"Faster Whisper model loaded: {model_size} on {device}")
        except ImportError:
            logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
            raise
    
    def transcribe(self, audio_path: str, language: str = "zh") -> Optional[str]:
        """
        Transcribe using Faster Whisper.
        
        Args:
            audio_path: Path to audio file
            language: Language code
            
        Returns:
            Transcribed text
        """
        try:
            logger.info(f"Transcribing audio with Faster Whisper: {audio_path}")
            
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
            )
            
            text = "".join([segment.text for segment in segments])
            logger.info(f"Transcription completed. Length: {len(text)} characters")
            return text
        
        except Exception as e:
            logger.error(f"Error transcribing with Faster Whisper: {e}")
            return None
