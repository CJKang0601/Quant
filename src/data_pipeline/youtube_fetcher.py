"""YouTube video fetcher using yt-dlp."""
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from src.utils.logger import get_logger
from src.utils.data_models import TranscriptionResult

logger = get_logger(__name__)


class YouTubeFetcher:
    """Fetches videos from YouTube channels."""
    
    def __init__(self, output_dir: str):
        """
        Initialize YouTube fetcher.
        
        Args:
            output_dir: Directory to save downloaded audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"YouTubeFetcher initialized with output_dir: {output_dir}")
    
    def fetch_latest_from_channel(self, channel_url: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch latest videos from a YouTube channel.
        
        Args:
            channel_url: YouTube channel URL
            max_results: Maximum number of videos to fetch
            
        Returns:
            List of video info dicts with 'url', 'title', 'date', 'video_id'
        """
        try:
            import yt_dlp
        except ImportError:
            logger.error("yt-dlp not installed. Install with: pip install yt-dlp")
            return []
        
        try:
            ydl_opts = {
                'quiet': False,
                'no_warnings': False,
                'extract_flat': 'in_playlist',
                'skip_unavailable_videos': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Fetching latest {max_results} videos from {channel_url}")
                result = ydl.extract_info(channel_url, download=False)
                
                videos = []
                for entry in result.get('entries', [])[:max_results]:
                    videos.append({
                        'url': f"https://www.youtube.com/watch?v={entry['id']}",
                        'title': entry.get('title', 'Unknown'),
                        'date': entry.get('upload_date', datetime.now().strftime('%Y%m%d')),
                        'video_id': entry['id'],
                        'duration': entry.get('duration', 0),
                    })
                
                logger.info(f"Found {len(videos)} videos from channel")
                return videos
        
        except Exception as e:
            logger.error(f"Error fetching from YouTube channel: {e}")
            return []
    
    def download_audio(self, video_url: str, video_title: str) -> Optional[str]:
        """
        Download audio from YouTube video.
        
        Args:
            video_url: YouTube video URL
            video_title: Video title for file naming
            
        Returns:
            Path to downloaded audio file, or None if failed
        """
        try:
            import yt_dlp
        except ImportError:
            logger.error("yt-dlp not installed")
            return None
        
        try:
            # Clean filename
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
            audio_path = self.output_dir / f"{safe_title}.mp3"
            
            # Skip if already downloaded
            if audio_path.exists():
                logger.info(f"Audio already exists: {audio_path}")
                return str(audio_path)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(self.output_dir / safe_title),
                'quiet': False,
                'no_warnings': False,
                # Try to bypass bot detection in GitHub Actions
                'nocheckcertificate': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.google.com/',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android_vr', 'web_embedded'],
                        'skip': ['dash', 'hls'],
                    }
                },
                'ignoreerrors': True, # Skip errors like members-only
            }
            
            logger.info(f"Downloading audio from: {video_url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                error_code = ydl.download([video_url])
                if error_code != 0:
                    logger.warning(f"Download failed with error code {error_code} for {video_url}")
            
            if audio_path.exists():
                logger.info(f"Audio saved to: {audio_path}")
                return str(audio_path)
            else:
                logger.error(f"Audio file not found after download: {audio_path}")
                return None
        
        except Exception as e:
            logger.error(f"Error downloading audio from {video_url}: {e}")
            return None
    
    def fetch_and_download(self, channel_url: str, max_results: int = 5) -> List[str]:
        """
        Fetch latest videos and download their audio.
        
        Args:
            channel_url: YouTube channel URL
            max_results: Maximum number of videos to process
            
        Returns:
            List of paths to downloaded audio files
        """
        videos = self.fetch_latest_from_channel(channel_url, max_results)
        audio_files = []
        
        import time
        for video in videos:
            audio_path = self.download_audio(video['url'], video['title'])
            if audio_path:
                audio_files.append(audio_path)
                logger.info(f"Successfully processed: {video['title']}")
            
            # 增加延遲避免被 Ban
            logger.info("Sleeping for 5 seconds between downloads...")
            time.sleep(5)
        
        logger.info(f"Downloaded {len(audio_files)} audio files")
        return audio_files
