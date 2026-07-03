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
        self.model_size = model_size
        self.device = device
        self._model = None

    @property
    def model(self):
        # 懶加載:處理字幕檔(.vtt/.srt)不需要模型,避免無謂下載模型權重
        if self._model is None:
            try:
                import whisper
            except ImportError:
                logger.error("openai-whisper not installed. Install with: pip install openai-whisper")
                raise
            self._model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"Whisper model loaded: {self.model_size} on {self.device}")
        return self._model
    
    def transcribe(self, audio_path: str, language: str = "zh") -> Optional[str]:
        """
        Transcribe audio file or read subtitle file.
        
        Args:
            audio_path: Path to audio or subtitle file
            language: Language code
            
        Returns:
            Text content or None if failed
        """
        # Handle subtitle files directly
        if audio_path.endswith(('.vtt', '.srt')):
            logger.info(f"Reading subtitle file: {audio_path}")
            try:
                with open(audio_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading subtitle file {audio_path}: {e}")
                return None

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
        """
        try:
            text = self.transcribe(audio_path, language)
            if not text:
                return None
            
            # Skip duration check for subtitle files to avoid FFmpeg dependency
            duration_seconds = 0
            if not audio_path.endswith(('.vtt', '.srt')):
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
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    @property
    def model(self):
        # 懶加載:處理字幕檔(.vtt/.srt)不需要模型
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
                raise
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info(f"Faster Whisper model loaded: {self.model_size} on {self.device}")
        return self._model
    
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
