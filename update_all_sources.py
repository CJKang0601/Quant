"""Script to update analysis for all configured sources."""
from main import MainPipeline
from config.settings import YOUTUBE_CHANNELS, PODCAST_FEEDS, DATA_PROCESSED_DIR
from src.utils.logger import get_logger
from datetime import datetime
from pathlib import Path

logger = get_logger(__name__)

def update_all():
    """Update analysis for all sources."""
    print("Starting update_all_sources.py...")
    pipeline = MainPipeline()
    
    # Ensure directories exist
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Process YouTube Channels
    for source_key, channel_url in YOUTUBE_CHANNELS.items():
        print(f"Checking YouTube source: {source_key} ({channel_url})")
        try:
            # 獲取最新影片並下載音訊
            audio_files = pipeline.youtube_fetcher.fetch_and_download(channel_url, max_results=1)
            print(f"Found {len(audio_files)} new audio files for {source_key}")
            
            for idx, audio_path in enumerate(audio_files):
                print(f"Processing audio: {audio_path}")
                # 處理音訊
                result = pipeline.data_pipeline.process_audio_file(
                    audio_path=audio_path,
                    source_id=f"{source_key}_{idx}",
                    source_type="youtube",
                    source_title=Path(audio_path).stem,
                )
                
                if result:
                    print(f"Analyzing content for {source_key}...")
                    # 分析
                    analysis = pipeline.agent.analyze(result, f"{source_key}_{idx}", Path(audio_path).stem)
                    
                    if analysis:
                        # 保存結果
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        output_path = DATA_PROCESSED_DIR / f"analysis_{source_key}_{timestamp}.json"
                        pipeline.formatter.save_analysis_json(analysis, str(output_path))
                        print(f"Saved analysis to {output_path}")
                else:
                    print(f"Failed to process audio for {source_key}")
        except Exception as e:
            print(f"Error updating YouTube source {source_key}: {e}")
            logger.error(f"Error updating YouTube source {source_key}: {e}")

    # 2. Process Podcast Feeds
    for source_key, feed_url in PODCAST_FEEDS.items():
        logger.info(f"Updating Podcast source: {source_key}")
        try:
            audio_files = pipeline.podcast_fetcher.fetch_and_download(feed_url, max_episodes=1)
            
            for idx, audio_path in enumerate(audio_files):
                result = pipeline.data_pipeline.process_audio_file(
                    audio_path=audio_path,
                    source_id=f"{source_key}_{idx}",
                    source_type="podcast",
                    source_title=Path(audio_path).stem,
                )
                
                if result:
                    analysis = pipeline.agent.analyze(result, f"{source_key}_{idx}", Path(audio_path).stem)
                    
                    if analysis:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        output_path = DATA_PROCESSED_DIR / f"analysis_{source_key}_{timestamp}.json"
                        pipeline.formatter.save_analysis_json(analysis, str(output_path))
                        logger.info(f"Successfully updated {source_key}")
        except Exception as e:
            logger.error(f"Error updating Podcast source {source_key}: {e}")

if __name__ == "__main__":
    update_all()
