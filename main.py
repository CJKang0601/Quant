"""Main entry point for AI Investment Agent."""
from pathlib import Path
from datetime import datetime

from src.data_pipeline.youtube_fetcher import YouTubeFetcher
from src.data_pipeline.podcast_fetcher import PodcastFetcher
from src.data_pipeline.preprocessor import TextPreprocessor, DataPipeline
from src.analysis_engine.agent import InvestmentAgent
from src.analysis_engine.output_formatter import OutputFormatter

from src.utils.logger import get_logger
from config.settings import DATA_RAW_DIR, DATA_PROCESSED_DIR, WHISPER_MODEL

logger = get_logger(__name__)


def _create_transcriber():
    """優先使用 faster-whisper(不需 torch、速度較快),失敗時退回 openai-whisper。"""
    try:
        from src.data_pipeline.transcriber import FasterWhisperTranscriber
        return FasterWhisperTranscriber(model_size=WHISPER_MODEL)
    except Exception as e:
        logger.warning(f"faster-whisper unavailable ({e}); falling back to openai-whisper")
        from src.data_pipeline.transcriber import WhisperTranscriber
        return WhisperTranscriber(model_size=WHISPER_MODEL)


class MainPipeline:
    """Main orchestration pipeline for entire workflow."""

    def __init__(self):
        """Initialize main pipeline."""
        self.youtube_fetcher = YouTubeFetcher(output_dir=str(DATA_RAW_DIR / "youtube"))
        self.podcast_fetcher = PodcastFetcher(output_dir=str(DATA_RAW_DIR / "podcast"))
        self.transcriber = _create_transcriber()
        self.preprocessor = TextPreprocessor()
        self.data_pipeline = DataPipeline(
            youtube_fetcher=self.youtube_fetcher,
            podcast_fetcher=self.podcast_fetcher,
            transcriber=self.transcriber,
            preprocessor=self.preprocessor,
        )
        self.agent = InvestmentAgent(llm_provider="openai")
        self.formatter = OutputFormatter()

        logger.info("MainPipeline initialized")

    def analyze_and_save(
        self,
        preprocessed,
        source_id: str,
        source_title: str,
        source_key: str = "",
        source_type: str = "youtube",
        content_date: str = None,
    ) -> bool:
        """Analyze preprocessed content and save the result JSON."""
        analysis = self.agent.analyze(
            preprocessed,
            source_id=source_id,
            source_title=source_title,
            source_key=source_key,
            source_type=source_type,
            content_date=content_date,
        )
        if not analysis:
            return False

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = source_key or source_id
        output_path = DATA_PROCESSED_DIR / f"analysis_{name}_{timestamp}.json"
        DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        self.formatter.save_analysis_json(analysis, str(output_path))
        print(self.formatter.format_for_display(analysis))
        return True

    def process_youtube_channel(self, channel_url: str, max_videos: int = 3) -> int:
        """
        Process latest videos from YouTube channel.

        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to process

        Returns:
            Number of successfully processed videos
        """
        logger.info(f"Processing YouTube channel: {channel_url}")

        audio_files = self.youtube_fetcher.fetch_and_download(channel_url, max_videos)
        logger.info(f"Downloaded {len(audio_files)} audio files from YouTube")

        processed_count = 0
        for idx, audio_path in enumerate(audio_files):
            try:
                result = self.data_pipeline.process_audio_file(
                    audio_path=audio_path,
                    source_id=f"youtube_{idx}",
                    source_type="youtube",
                    source_title=Path(audio_path).stem,
                )
                if result and self.analyze_and_save(
                    result, f"youtube_{idx}", Path(audio_path).stem, source_type="youtube"
                ):
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing YouTube video {idx}: {e}")

        return processed_count

    def process_podcast_feed(self, feed_url: str, max_episodes: int = 3) -> int:
        """
        Process latest episodes from podcast feed.

        Args:
            feed_url: Podcast RSS feed URL
            max_episodes: Maximum number of episodes to process

        Returns:
            Number of successfully processed episodes
        """
        logger.info(f"Processing podcast feed: {feed_url}")

        audio_files = self.podcast_fetcher.fetch_and_download(feed_url, max_episodes)
        logger.info(f"Downloaded {len(audio_files)} audio files from podcast")

        processed_count = 0
        for idx, audio_path in enumerate(audio_files):
            try:
                result = self.data_pipeline.process_audio_file(
                    audio_path=audio_path,
                    source_id=f"podcast_{idx}",
                    source_type="podcast",
                    source_title=Path(audio_path).stem,
                )
                if result and self.analyze_and_save(
                    result, f"podcast_{idx}", Path(audio_path).stem, source_type="podcast"
                ):
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing podcast episode {idx}: {e}")

        return processed_count

    def process_local_audio(self, audio_path: str, source_type: str = "unknown") -> bool:
        """
        Process a local audio file.

        Args:
            audio_path: Path to audio file
            source_type: Type of source ('youtube', 'podcast', 'unknown')

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Processing local audio: {audio_path}")

        try:
            stem = Path(audio_path).stem
            result = self.data_pipeline.process_audio_file(
                audio_path=audio_path,
                source_id=stem,
                source_type=source_type,
                source_title=stem,
            )
            if result:
                return self.analyze_and_save(result, stem, stem, source_type=source_type)
        except Exception as e:
            logger.error(f"Error processing local audio: {e}")

        return False


def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("AI INVESTMENT AGENT - MAIN PIPELINE")
    logger.info("=" * 80)

    pipeline = MainPipeline()

    # Example: Process local audio file
    # pipeline.process_local_audio("path/to/audio.mp3", source_type="youtube")

    # Example: Process YouTube channel
    # pipeline.process_youtube_channel("https://www.youtube.com/@YourChannel", max_videos=3)

    # Example: Process podcast feed
    # pipeline.process_podcast_feed("https://example.com/podcast/feed.xml", max_episodes=3)

    print("\nAI Investment Agent Ready!")
    print("Configuration complete. Ready to process audio content.")
    print(f"Data saved to: {DATA_PROCESSED_DIR}")


if __name__ == "__main__":
    main()
