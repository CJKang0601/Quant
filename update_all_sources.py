"""Script to update analysis for all configured sources.

以 data/processed_manifest.json 記錄已處理的影片/集數 ID(隨 repo 提交),
避免 CI 每天重新下載、重新轉錄、重新分析同樣的內容。
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

from main import MainPipeline
from config.settings import (
    YOUTUBE_CHANNELS,
    PODCAST_FEEDS,
    DATA_PROCESSED_DIR,
    PROCESSED_MANIFEST_PATH,
    FFMPEG_PATH,
)
from src.utils.logger import get_logger

# Add FFmpeg to PATH
if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ["PATH"]

logger = get_logger(__name__)

MAX_ITEMS_PER_SOURCE = 5
MANIFEST_KEEP_PER_SOURCE = 200  # 每個來源保留的已處理 ID 數量上限


def load_manifest() -> dict:
    """載入已處理清單;不存在或壞損時回傳空清單。"""
    try:
        with open(PROCESSED_MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            if isinstance(manifest, dict):
                return manifest
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.warning(f"Could not read manifest, starting fresh: {e}")
    return {}


def save_manifest(manifest: dict) -> None:
    PROCESSED_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    trimmed = {k: v[-MANIFEST_KEEP_PER_SOURCE:] for k, v in manifest.items()}
    with open(PROCESSED_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


def mark_processed(manifest: dict, source_key: str, item_id: str) -> None:
    manifest.setdefault(source_key, []).append(item_id)
    save_manifest(manifest)


def format_upload_date(raw: str) -> str:
    """yt-dlp 的 upload_date 是 YYYYMMDD,轉成 YYYY-MM-DD。"""
    if raw and len(raw) == 8 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return None


def update_youtube_source(pipeline, manifest, source_key, channel_url) -> int:
    """處理單一 YouTube 來源,回傳成功分析的數量。"""
    print(f"Checking YouTube source: {source_key} ({channel_url})")
    processed = 0

    videos = pipeline.youtube_fetcher.fetch_latest_from_channel(channel_url, MAX_ITEMS_PER_SOURCE)
    done = set(manifest.get(source_key, []))
    new_videos = [v for v in videos if v["video_id"] not in done]
    print(f"{source_key}: {len(videos)} candidates, {len(new_videos)} new")

    for video in new_videos:
        try:
            audio_path = pipeline.youtube_fetcher.download_audio(video["url"], video["title"])
            time.sleep(5)  # 下載間隔,避免被 ban
            if not audio_path:
                # 沒抓到字幕/音檔:不標記為已處理,下次執行再重試
                print(f"{source_key}: no subtitles/audio for '{video['title']}', will retry next run")
                continue

            result = pipeline.data_pipeline.process_audio_file(
                audio_path=audio_path,
                source_id=f"{source_key}_{video['video_id']}",
                source_type="youtube",
                source_title=video["title"],
            )
            if not result:
                print(f"{source_key}: failed to process '{video['title']}'")
                continue

            print(f"Analyzing: {video['title']}")
            ok = pipeline.analyze_and_save(
                result,
                source_id=f"{source_key}_{video['video_id']}",
                source_title=video["title"],
                source_key=source_key,
                source_type="youtube",
                content_date=format_upload_date(video.get("date", "")),
            )
            if ok:
                mark_processed(manifest, source_key, video["video_id"])
                processed += 1
        except Exception as e:
            logger.error(f"Error processing {source_key} video '{video.get('title')}': {e}")

    return processed


def update_podcast_source(pipeline, manifest, source_key, feed_url) -> int:
    """處理單一 Podcast 來源,回傳成功分析的數量。"""
    print(f"Checking Podcast source: {source_key}")
    processed = 0

    episodes = pipeline.podcast_fetcher.fetch_feed(feed_url, MAX_ITEMS_PER_SOURCE)
    done = set(manifest.get(source_key, []))
    new_episodes = [e for e in episodes if e["guid"] not in done]
    print(f"{source_key}: {len(episodes)} candidates, {len(new_episodes)} new")

    for episode in new_episodes:
        try:
            audio_path = pipeline.podcast_fetcher.download_episode(
                episode["audio_url"], episode["title"]
            )
            time.sleep(5)
            if not audio_path:
                continue

            result = pipeline.data_pipeline.process_audio_file(
                audio_path=audio_path,
                source_id=f"{source_key}_{episode['guid'][:24]}",
                source_type="podcast",
                source_title=episode["title"],
            )
            if not result:
                continue

            print(f"Analyzing: {episode['title']}")
            ok = pipeline.analyze_and_save(
                result,
                source_id=f"{source_key}_{episode['guid'][:24]}",
                source_title=episode["title"],
                source_key=source_key,
                source_type="podcast",
                content_date=episode.get("published_date"),
            )
            if ok:
                mark_processed(manifest, source_key, episode["guid"])
                processed += 1
        except Exception as e:
            logger.error(f"Error processing {source_key} episode '{episode.get('title')}': {e}")

    return processed


def update_all():
    """Update analysis for all sources."""
    print("Starting update_all_sources.py...")
    pipeline = MainPipeline()
    manifest = load_manifest()
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for source_key, channel_url in YOUTUBE_CHANNELS.items():
        try:
            total += update_youtube_source(pipeline, manifest, source_key, channel_url)
        except Exception as e:
            logger.error(f"Error updating YouTube source {source_key}: {e}")

    for source_key, feed_url in PODCAST_FEEDS.items():
        try:
            total += update_podcast_source(pipeline, manifest, source_key, feed_url)
        except Exception as e:
            logger.error(f"Error updating Podcast source {source_key}: {e}")

    print(f"Done. {total} new analyses generated at {datetime.now().isoformat()}")


if __name__ == "__main__":
    update_all()
