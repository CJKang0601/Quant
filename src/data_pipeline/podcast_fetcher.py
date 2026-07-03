"""Podcast fetcher using RSS feeds."""
import feedparser
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PodcastFetcher:
    """Fetches podcast episodes from RSS feeds."""
    
    def __init__(self, output_dir: str):
        """
        Initialize podcast fetcher.
        
        Args:
            output_dir: Directory to save downloaded audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PodcastFetcher initialized with output_dir: {output_dir}")
    
    def fetch_feed(self, feed_url: str, max_episodes: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch episodes from RSS feed.
        
        Args:
            feed_url: RSS feed URL
            max_episodes: Maximum number of episodes to fetch
            
        Returns:
            List of episode info dicts
        """
        try:
            logger.info(f"Fetching feed from: {feed_url}")
            # Use requests with User-Agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(feed_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Use text instead of content to avoid encoding/malformed issues
            feed = feedparser.parse(response.text)
            
            if feed.bozo:
                logger.warning(f"Feed parsing issues: {feed.bozo_exception}")
            
            episodes = []
            for entry in feed.entries[:max_episodes]:
                published_parsed = entry.get('published_parsed')
                published_date = (
                    f"{published_parsed.tm_year:04d}-{published_parsed.tm_mon:02d}-{published_parsed.tm_mday:02d}"
                    if published_parsed else None
                )
                episode = {
                    'title': entry.get('title', 'Unknown'),
                    'description': entry.get('summary', ''),
                    'published': entry.get('published', datetime.now().isoformat()),
                    'published_date': published_date,  # YYYY-MM-DD,趨勢時間軸用
                    'guid': entry.get('id', '') or entry.get('link', ''),  # 去重用
                    'link': entry.get('link', ''),
                    'audio_url': None,
                }
                
                # Look for audio in enclosures or links
                if hasattr(entry, 'enclosures'):
                    for enclosure in entry.enclosures:
                        if 'audio' in enclosure.get('type', '').lower():
                            episode['audio_url'] = enclosure.href
                            break
                
                # Alternative: look in links
                if not episode['audio_url'] and hasattr(entry, 'links'):
                    for link in entry.links:
                        if link.get('type', '').startswith('audio'):
                            episode['audio_url'] = link.href
                            break
                
                if episode['audio_url']:
                    if not episode['guid']:
                        episode['guid'] = episode['audio_url']
                    episodes.append(episode)
            
            logger.info(f"Found {len(episodes)} episodes with audio")
            return episodes
        
        except Exception as e:
            logger.error(f"Error fetching feed from {feed_url}: {e}")
            return []
    
    def download_episode(self, audio_url: str, episode_title: str) -> Optional[str]:
        """
        Download podcast episode audio.
        
        Args:
            audio_url: Direct URL to audio file
            episode_title: Episode title for file naming
            
        Returns:
            Path to downloaded audio file, or None if failed
        """
        try:
            # Clean filename
            safe_title = "".join(c for c in episode_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
            
            # Determine file extension from URL
            ext = '.mp3'
            if '.m4a' in audio_url:
                ext = '.m4a'
            elif '.wav' in audio_url:
                ext = '.wav'
            
            audio_path = self.output_dir / f"{safe_title}{ext}"
            
            # Skip if already downloaded
            if audio_path.exists():
                logger.info(f"Audio already exists: {audio_path}")
                return str(audio_path)
            
            logger.info(f"Downloading podcast episode: {episode_title}")
            # 整集音檔可能上百 MB,串流寫入避免整檔進記憶體
            with requests.get(audio_url, timeout=60, stream=True) as response:
                response.raise_for_status()
                with open(audio_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        f.write(chunk)
            
            logger.info(f"Podcast audio saved to: {audio_path}")
            return str(audio_path)
        
        except Exception as e:
            logger.error(f"Error downloading podcast episode from {audio_url}: {e}")
            return None
    
    def fetch_and_download(self, feed_url: str, max_episodes: int = 5) -> List[str]:
        """
        Fetch latest episodes and download their audio.
        
        Args:
            feed_url: RSS feed URL
            max_episodes: Maximum number of episodes to process
            
        Returns:
            List of paths to downloaded audio files
        """
        episodes = self.fetch_feed(feed_url, max_episodes)
        audio_files = []
        
        import time
        for episode in episodes:
            if episode['audio_url']:
                audio_path = self.download_episode(episode['audio_url'], episode['title'])
                if audio_path:
                    audio_files.append(audio_path)
                    logger.info(f"Successfully processed: {episode['title']}")
                
                # 增加延遲避免被 Ban
                logger.info("Sleeping for 5 seconds between podcast downloads...")
                time.sleep(5)
        
        logger.info(f"Downloaded {len(audio_files)} podcast episodes")
        return audio_files
