"""
Utilidades de base de datos
"""
import sqlite3
import os
import secrets
from flask import session, jsonify, request
from backend.config import Config


def init_db():
    """Inicializar la base de datos"""
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Configurar modo WAL para mejor concurrencia
    cursor.execute('PRAGMA journal_mode=WAL;')
    
    # Tabla de búsqueda de transcripciones
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
    
    conn.commit()
    conn.close()


def generate_csrf_token():
    """Generar token CSRF"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']


def csrf_protect():
    """Protección CSRF para peticiones POST"""
    if request.method == "POST":
        exempt_endpoints = [] 
        if request.endpoint in exempt_endpoints:
            return

        token = session.get('csrf_token')
        if not token:
            token = secrets.token_hex(16)
            session['csrf_token'] = token
            
        req_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
        
        # Debug CSRF
        # print(f"DEBUG: Session token: {token}")
        # print(f"DEBUG: Request token: {req_token}")
        
        if not req_token or req_token != token:
            return jsonify({'error': 'CSRF token missing or incorrect'}), 403
