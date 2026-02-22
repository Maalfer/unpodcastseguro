"""
Blueprint de API
Maneja todos los endpoints de API públicos
"""
import os
import json
import sys
import subprocess
import threading
import re
from flask import Blueprint, jsonify, request
from backend.config import Config
from backend.utils import load_json_file, save_json_file
import requests
from backend.ai import search_transcripts, generate_answer

api_bp = Blueprint('api', __name__)

# Directorio base del proyecto
BASE_DIR = Config.BASE_DIR


# ==================== SUPABASE ====================

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')


def call_supabase(method, table, data=None, filters=None):
    """Llamar a la API de Supabase"""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    try:
        headers = {
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
            'apikey': SUPABASE_ANON_KEY
        }

        url = f"{SUPABASE_URL}/rest/v1/{table}"

        if method == 'GET':
            if filters:
                query_string = '&'.join([f"{k}=eq.{v}" for k, v in filters.items()])
                url += f"?{query_string}"
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)

        return response.json() if response.status_code in [200, 201] else None
    except Exception as e:
        print(f"Supabase error: {e}")
        return None


@api_bp.route('/participation', methods=['POST'])
def api_participation():
    """Recibir formulario de participación"""
    try:
        data = request.get_json()

        result = call_supabase('POST', 'participation_forms', {
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'message': data.get('message')
        })

        if result:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to save'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/guests', methods=['GET'])
def api_guests():
    """Obtener lista de invitados"""
    try:
        result = call_supabase('GET', 'guests')
        return jsonify(result or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/newsletters', methods=['GET'])
def api_newsletters():
    """Obtener newsletters"""
    try:
        result = call_supabase('GET', 'newsletter_emails')
        return jsonify(result or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/awards', methods=['GET'])
def api_awards():
    """Obtener premios"""
    try:
        result = call_supabase('GET', 'awards')
        return jsonify(result or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== AI CHAT ====================

@api_bp.route('/chat', methods=['POST'])
def api_chat():
    """Chat con IA usando RAG"""
    try:
        data = request.get_json()
        query = data.get('message')
        
        if not query:
            return jsonify({'error': 'No message provided'}), 400
            
        # 1. Buscar contexto relevante
        context = search_transcripts(query)
        
        # 2. Generar respuesta
        answer = generate_answer(query, context)
        
        return jsonify({
            'answer': answer,
            'sources': context
        })
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== JSON DATA ====================

@api_bp.route('/recommendations', methods=['GET'])
def api_recommendations():
    """Obtener recomendaciones"""
    try:
        data = load_json_file(Config.RECOMENDACIONES_JSON, default=[])
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/episodios')
def api_episodios():
    """Obtener lista de episodios"""
    try:
        data = load_json_file(Config.EPISODIOS_JSON, default=[])
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== YOUTUBE & TRANSCRIPTS ====================

def sanitize_filename(name):
    """Sanitizar nombre de archivo"""
    return re.sub(r'[\\/*?:"<>|]', "", name)


def clean_transcript_text(raw_text):
    """Limpiar texto de transcripción"""
    lines = raw_text.splitlines()
    cleaned_lines = []
    last_line = ""
    
    for line in lines:
        line = line.strip()
        if (not line or 
            line.startswith('WEBVTT') or 
            line.startswith('Kind:') or 
            line.startswith('Language:') or 
            '-->' in line or 
            line.isdigit()):
            continue
        
        line = re.sub(r'<[^>]+>', '', line)
        line = line.strip()
        
        if not line or line == last_line:
            continue
            
        cleaned_lines.append(line)
        last_line = line
        
    return " ".join(cleaned_lines)


def download_transcripts_background(videos):
    """Descargar transcripciones en segundo plano"""
    yt_dlp_path = os.path.join(BASE_DIR, 'yt-dlp')
    
    for video in videos:
        video_id = video['id']
        title = video['title']
        safe_title = sanitize_filename(title)
        txt_filename = f"{safe_title}.txt"
        txt_path = os.path.join(Config.TRANSCRIPTS_FOLDER, txt_filename)
        
        if os.path.exists(txt_path):
            continue
            
        print(f"Downloading transcript for: {title}")
        
        try:
            cmd = [
                sys.executable,
                yt_dlp_path,
                '--write-auto-sub',
                '--write-sub',
                '--sub-lang', 'es,en',
                '--skip-download',
                '--convert-subs', 'srt',
                '--output', os.path.join(Config.TRANSCRIPTS_FOLDER, safe_title),
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            downloaded_file = None
            for f in os.listdir(Config.TRANSCRIPTS_FOLDER):
                if f.startswith(safe_title) and (f.endswith('.srt') or f.endswith('.vtt')):
                    downloaded_file = os.path.join(Config.TRANSCRIPTS_FOLDER, f)
                    break
            
            if downloaded_file:
                with open(downloaded_file, 'r', encoding='utf-8') as f_in:
                    raw_content = f_in.read()
                
                clean_text = clean_transcript_text(raw_content)
                
                with open(txt_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(clean_text)
                
                os.remove(downloaded_file)
                print(f"Saved transcript: {txt_filename}")
                
        except Exception as e:
            print(f"Error processing transcript for {title}: {e}")


@api_bp.route('/youtube_videos')
def api_youtube_videos():
    """Obtener videos de YouTube (desde caché)"""
    try:
        # Los videos son actualizados por scripts/sync_transcripts.py en data/videos.json
        videos_json_path = os.path.join(Config.DATA_FOLDER, 'videos.json')
        
        # Si no existe en data/, intentar en static/ para retrocompatibilidad temporal
        if not os.path.exists(videos_json_path):
            videos_json_path = os.path.join(Config.STATIC_FOLDER, 'videos.json')
            
        data = load_json_file(videos_json_path, default=[])
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching YouTube videos: {e}")
        return jsonify([])


@api_bp.route('/sync_status')
def api_sync_status():
    """Obtener estado de sincronización"""
    if os.path.exists(Config.SYNC_LOG_PATH):
        try:
            data = load_json_file(Config.SYNC_LOG_PATH)
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({
            'last_sync': None,
            'total_videos': 0,
            'new_videos_found': 0,
            'transcripts_downloaded': 0
        })
