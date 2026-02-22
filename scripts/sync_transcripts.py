#!/usr/bin/env python3
"""
Script to synchronize YouTube video transcriptions
Detects new videos from the channel and downloads their transcripts
"""

import sys
import os
import glob

# Configure dependency paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
site_packages = glob.glob(os.path.join(base_dir, 'librerias/lib/python*/site-packages'))
if site_packages:
    sys.path.insert(0, site_packages[0])

import sqlite3
import json
import subprocess
import re
import fcntl
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../sync_debug.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TRANSCRIPTS_FOLDER = os.path.join(BASE_DIR, 'database', 'transcripts')
VIDEOS_JSON_PATH = os.path.join(BASE_DIR, 'static', 'data', 'videos.json')
SYNC_LOG_PATH = os.path.join(BASE_DIR, 'sync_log.json')

DB_PATH = os.path.join(BASE_DIR, 'database', 'usuarios.db')

# YouTube playlist
YOUTUBE_CHANNEL_URL = 'https://www.youtube.com/playlist?list=PLnuadL3Xteo2BlcWFfbl7-BiimziNkFkS'

def sanitize_filename(name):
    """Remove invalid characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def clean_transcript_text(raw_text):
    """Cleans WebVTT/SRT content to plain text"""
    lines = raw_text.splitlines()
    cleaned_lines = []
    last_line = ""
    
    for line in lines:
        line = line.strip()
        # Skip headers, metadata, and timestamps
        if (not line or 
            line.startswith('WEBVTT') or 
            line.startswith('Kind:') or 
            line.startswith('Language:') or 
            '-->' in line or 
            line.isdigit()):
            continue
        
        # Remove HTML-like tags
        line = re.sub(r'<[^>]+>', '', line)
        line = line.strip()
        
        if not line:
            continue
            
        # Deduplicate consecutive identical lines
        if line == last_line:
            continue
            
        cleaned_lines.append(line)
        last_line = line
        
    return " ".join(cleaned_lines)

def get_youtube_videos():
    """Fetch latest videos from YouTube channel using yt-dlp"""
    logging.info("Obteniendo videos del canal...")
    
    command = [
        sys.executable,
        '-m', 'yt_dlp',
        '--dump-json',
        '--flat-playlist',
        '--playlist-end', '1000',
        YOUTUBE_CHANNEL_URL
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            logging.error(f"Error ejecutando yt-dlp: {result.stderr}")
            return []

        videos = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            try:
                entry = json.loads(line)
                
                video_id = entry.get('id')
                title = entry.get('title')
                url = entry.get('url') or entry.get('webpage_url')
                
                # Filter out Shorts and Private videos
                if url and '/shorts/' in url:
                    continue
                if title and '[Private video]' in title:
                    continue
                
                thumbnail = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                
                videos.append({
                    'id': video_id,
                    'title': title,
                    'link': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': thumbnail,
                    'published': ''
                })
            except json.JSONDecodeError:
                continue
        
        logging.info(f"{len(videos)} videos encontrados")
        return videos
        
    except subprocess.TimeoutExpired:
        logging.error("Timeout al obtener videos de YouTube")
        return []
    except Exception as e:
        logging.error(f"Error al obtener videos: {e}")
        return []

def load_existing_videos():
    """Load existing videos from videos.json"""
    if os.path.exists(VIDEOS_JSON_PATH):
        try:
            with open(VIDEOS_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error cargando videos.json: {e}")
            return []
    return []

def save_videos(videos):
    """Save videos list to videos.json"""
    try:
        os.makedirs(os.path.dirname(VIDEOS_JSON_PATH), exist_ok=True)
        with open(VIDEOS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        logging.info("videos.json actualizado")
    except Exception as e:
        logging.error(f"Error guardando videos.json: {e}")

def download_transcript(video):
    """Download transcript for a single video"""
    video_id = video['id']
    title = video['title']
    safe_title = sanitize_filename(title)
    txt_filename = f"{safe_title}.txt"
    txt_path = os.path.join(TRANSCRIPTS_FOLDER, txt_filename)
    
    # Skip if already exists
    if os.path.exists(txt_path):
        return False
        
    logging.info(f"Descargando transcripción: {title}")
    
    try:
        # Ensure transcripts folder exists
        os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)
        
        cmd = [
            sys.executable,
            '-m', 'yt_dlp',
            '--write-auto-sub',
            '--write-sub',
            '--sub-lang', 'es,en',
            '--skip-download',
            '--convert-subs', 'srt',
            '--output', os.path.join(TRANSCRIPTS_FOLDER, safe_title),
            f"https://www.youtube.com/watch?v={video_id}"
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        
        # Find downloaded file
        downloaded_file = None
        for f in os.listdir(TRANSCRIPTS_FOLDER):
            if f.startswith(safe_title) and (f.endswith('.srt') or f.endswith('.vtt')):
                downloaded_file = os.path.join(TRANSCRIPTS_FOLDER, f)
                break
        
        if downloaded_file:
            with open(downloaded_file, 'r', encoding='utf-8') as f_in:
                raw_content = f_in.read()
            
            clean_text = clean_transcript_text(raw_content)
            
            with open(txt_path, 'w', encoding='utf-8') as f_out:
                f_out.write(clean_text)
            
            # Cleanup original subtitle file
            os.remove(downloaded_file)
            logging.info(f"✓ Transcripción guardada: {txt_filename}")
            return True
        else:
            logging.warning(f"✗ No se encontró transcripción para: {title}")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout descargando: {title}")
        return False
    except Exception as e:
        logging.error(f"Error procesando {title}: {e}")
        return False

def update_search_index(filename, title, content, url, published=""):
    """Update FTS5 index for a transcript"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Ensure table exists (duplicate of app.py logic to be safe)
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS transcripts_search USING fts5(
                filename,
                title,
                content,
                url,
                published,
                tokenize='porter'
            );
        ''')
        
        # Remove existing entry
        cursor.execute('DELETE FROM transcripts_search WHERE filename = ?', (filename,))
        
        # Insert
        cursor.execute('''
            INSERT INTO transcripts_search (filename, title, content, url, published)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, title, content, url, published))
        
        conn.commit()
        conn.close()
        # logging.info(f"Indexed: {filename}") 
    except Exception as e:
        logging.error(f"Error updating search index for {filename}: {e}")

def sync_transcripts():
    """Main synchronization function"""
    lock_path = os.path.join(BASE_DIR, 'sync.lock')
    lock_file = open(lock_path, 'w')
    
    try:
        # Try to acquire an exclusive lock (non-blocking)
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        logging.warning("Another instance is running. Exiting.")
        return

    try:
        logging.info(f"{'='*60}")
        logging.info("INICIANDO SINCRONIZACIÓN")
        logging.info(f"{'='*60}")
        
        # Get current videos from YouTube
        current_videos = get_youtube_videos()
        
        if not current_videos:
            logging.warning("No se obtuvieron videos del canal")
            return
        
        # Load existing videos
        existing_videos = load_existing_videos()
        existing_ids = {v['id'] for v in existing_videos}
        
        # Find new videos
        new_videos = [v for v in current_videos if v['id'] not in existing_ids]
        
        logging.info(f"Videos existentes: {len(existing_videos)}")
        logging.info(f"Videos nuevos detectados: {len(new_videos)}")
        
        # Download transcripts for ALL videos that don't have a transcript yet
        downloaded_count = 0
        missing_transcripts = []
        
        # Also reuse this loop to ensure everything is indexed
        indexed_count = 0
        
        for video in current_videos:
            safe_title = sanitize_filename(video['title'])
            txt_filename = f"{safe_title}.txt"
            txt_path = os.path.join(TRANSCRIPTS_FOLDER, txt_filename)
            
            # Check if transcript exists
            if not os.path.exists(txt_path):
                missing_transcripts.append(video)
            else:
                # If it exists, ensure it's indexed
                try:
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    update_search_index(
                        txt_filename, 
                        video['title'], 
                        content, 
                        video['link'], 
                        video.get('published', '')
                    )
                    indexed_count += 1
                except Exception as e:
                    logging.error(f"Error indexing existing file {txt_filename}: {e}")
        
        logging.info(f"Transcripciones faltantes: {len(missing_transcripts)}")
        
        for video in missing_transcripts:
            if download_transcript(video):
                downloaded_count += 1
                # Read the newly downloaded file and index
                safe_title = sanitize_filename(video['title'])
                txt_filename = f"{safe_title}.txt"
                txt_path = os.path.join(TRANSCRIPTS_FOLDER, txt_filename)
                if os.path.exists(txt_path):
                     with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                     update_search_index(
                        txt_filename, 
                        video['title'], 
                        content, 
                        video['link'], 
                        video.get('published', '')
                    )
                     indexed_count += 1
        
        # Update videos.json with all current videos
        save_videos(current_videos)
        
        # Save sync log
        sync_data = {
            'last_sync': datetime.now().isoformat(),
            'total_videos': len(current_videos),
            'new_videos_found': len(new_videos),
            'missing_transcripts': len(missing_transcripts),
            'transcripts_downloaded': downloaded_count
        }
        
        try:
            with open(SYNC_LOG_PATH, 'w', encoding='utf-8') as f:
                json.dump(sync_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error guardando log de sincronización: {e}")
        
        logging.info(f"{'='*60}")
        logging.info("SINCRONIZACIÓN COMPLETADA")
        logging.info(f"  - Transcripciones descargadas: {downloaded_count}")
        logging.info(f"  - Videos indexados en buscador: {indexed_count}")
        logging.info(f"  - Total videos en videos.json: {len(current_videos)}")
        logging.info(f"{'='*60}")

    except Exception as e:
        logging.error(f"Error fatal en sincronización: {e}", exc_info=True)
    finally:
        # Release lock
        fcntl.lockf(lock_file, fcntl.LOCK_UN)
        lock_file.close()

if __name__ == '__main__':
    sync_transcripts()
