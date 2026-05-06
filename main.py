"""Main entry point for AI Investment Agent."""
import json
from pathlib import Path
from datetime import datetime

from src.data_pipeline.youtube_fetcher import YouTubeFetcher
from src.data_pipeline.podcast_fetcher import PodcastFetcher
from src.data_pipeline.transcriber import WhisperTranscriber
from src.data_pipeline.preprocessor import TextPreprocessor, DataPipeline
from src.analysis_engine.agent import InvestmentAgent
from src.analysis_engine.output_formatter import OutputFormatter

from src.utils.logger import get_logger
from config.settings import DATA_RAW_DIR, DATA_PROCESSED_DIR

logger = get_logger(__name__)


class MainPipeline:
    """Main orchestration pipeline for entire workflow."""
    
    def __init__(self):
        """Initialize main pipeline."""
        self.youtube_fetcher = YouTubeFetcher(output_dir=str(DATA_RAW_DIR / "youtube"))
        self.podcast_fetcher = PodcastFetcher(output_dir=str(DATA_RAW_DIR / "podcast"))
        self.transcriber = WhisperTranscriber(model_size="base")
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
        
        # Fetch and download
        audio_files = self.youtube_fetcher.fetch_and_download(channel_url, max_videos)
        logger.info(f"Downloaded {len(audio_files)} audio files from YouTube")
        
        processed_count = 0
        for idx, audio_path in enumerate(audio_files):
            try:
                # Process through pipeline
                result = self.data_pipeline.process_audio_file(
                    audio_path=audio_path,
                    source_id=f"youtube_{idx}",
                    source_type="youtube",
                    source_title=Path(audio_path).stem,
                )
                
                if result:
                    # Analyze
                    analysis = self.agent.analyze(result, f"youtube_{idx}", Path(audio_path).stem)
                    
                    if analysis:
                        # Save results
                        output_path = DATA_PROCESSED_DIR / f"youtube_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        self.formatter.save_analysis_json(analysis, str(output_path))
                        
                        # Print summary
                        print(self.formatter.format_for_display(analysis))
                        
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
        
        # Fetch and download
        audio_files = self.podcast_fetcher.fetch_and_download(feed_url, max_episodes)
        logger.info(f"Downloaded {len(audio_files)} audio files from podcast")
        
        processed_count = 0
        for idx, audio_path in enumerate(audio_files):
            try:
                # Process through pipeline
                result = self.data_pipeline.process_audio_file(
                    audio_path=audio_path,
                    source_id=f"podcast_{idx}",
                    source_type="podcast",
                    source_title=Path(audio_path).stem,
                )
                
                if result:
                    # Analyze
                    analysis = self.agent.analyze(result, f"podcast_{idx}", Path(audio_path).stem)
                    
                    if analysis:
                        # Save results
                        output_path = DATA_PROCESSED_DIR / f"podcast_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        self.formatter.save_analysis_json(analysis, str(output_path))
                        
                        # Print summary
                        print(self.formatter.format_for_display(analysis))
                        
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
            # Process through pipeline
            result = self.data_pipeline.process_audio_file(
                audio_path=audio_path,
                source_id=Path(audio_path).stem,
                source_type=source_type,
                source_title=Path(audio_path).stem,
            )
            
            if result:
                # Analyze
                analysis = self.agent.analyze(
                    result,
                    Path(audio_path).stem,
                    Path(audio_path).stem
                )
                
                if analysis:
                    # Save results
                    output_path = DATA_PROCESSED_DIR / f"{Path(audio_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    self.formatter.save_analysis_json(analysis, str(output_path))
                    
                    # Print summary
                    print(self.formatter.format_for_display(analysis))
                    
                    return True
        
        except Exception as e:
            logger.error(f"Error processing local audio: {e}")
        
        return False


def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("AI INVESTMENT AGENT - MAIN PIPELINE")
    logger.info("=" * 80)
    
    # Initialize pipeline
    pipeline = MainPipeline()
    
    # Example: Process local audio file
    # Uncomment and modify with your audio file path
    # pipeline.process_local_audio("path/to/audio.mp3", source_type="youtube")
    
    # Example: Process YouTube channel
    # youtube_url = "https://www.youtube.com/@YourChannel"
    # pipeline.process_youtube_channel(youtube_url, max_videos=3)
    
    # Example: Process podcast feed
    # podcast_rss = "https://example.com/podcast/feed.xml"
    # pipeline.process_podcast_feed(podcast_rss, max_episodes=3)
    
    print("\nAI Investment Agent Ready!")
    print("Configuration complete. Ready to process audio content.")
    print(f"Data saved to: {DATA_PROCESSED_DIR}")


if __name__ == "__main__":
    main()
