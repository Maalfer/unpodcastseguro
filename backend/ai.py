"""
Módulo de IA para Un Podcast Seguro
Implementa RAG (Retrieval Augmented Generation) usando Gemini y SQLite FTS5
"""
import os
import json
import sqlite3
from google import genai
from backend.config import Config

# Configurar Gemini
client = None
if Config.GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring Gemini client: {e}")
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def load_episode_metadata():
    """Cargar metadatos de todos los episodios desde videos.json"""
    try:
        json_path = os.path.join(Config.DATA_FOLDER, 'videos.json')
        if not os.path.exists(json_path):
            return ""
            
        with open(json_path, 'r', encoding='utf-8') as f:
            videos = json.load(f)
            
        # Formatear lista compacta para el contexto
        lines = ["LISTADO COMPLETO DE EPISODIOS (Úsalo para listar, ordenar o contar):"]
        for v in videos:
            lines.append(f"- ID: {v.get('id')} | Título: {v.get('title')} | Publicado: {v.get('published', 'N/A')}")
        return "\n".join(lines)
    except Exception as e:
        print(f"Error cargando metadatos de episodios: {e}")
        return ""

def search_transcripts(query, limit=5):
    """
    Buscar en las transcripciones usando FTS5
    
    Args:
        query (str): Consulta del usuario
        limit (int): Número máximo de resultados
        
    Returns:
        list: Lista de diccionarios con los resultados
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar en la tabla virtual FTS5
        # Usamos snippet() para obtener un fragmento relevante con el término de búsqueda
        cursor.execute('''
            SELECT 
                title,
                url,
                published,
                snippet(transcripts_search, 2, '<b>', '</b>', '...', 64) as fragment,
                rank
            FROM transcripts_search 
            WHERE transcripts_search MATCH ? 
            ORDER BY rank 
            LIMIT ?
        ''', (query, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        print(f"Error en búsqueda FTS5: {e}")
        return []

def generate_answer(query, context):
    """
    Generar respuesta usando Gemini
    
    Args:
        query (str): Pregunta del usuario
        context (list): Lista de resultados de la búsqueda
        
    Returns:
        str: Respuesta generada
    """
    if not client:
        return "Error: Cliente de Gemini no configurado (API Key faltante)."

    try:
        # Cargar contexto global de episodios
        global_episodes = load_episode_metadata()

        # Construir el prompt con el contexto
        context_text = "\n\n".join([
            f"Fragmento relevante ({res['title']}): ...{res['fragment']}..." 
            for res in context
        ])
        
        prompt = f"""
        Actúa como un asistente experto en ciberseguridad para "Un Podcast Seguro".
        
        TIENES A TU DISPOSICIÓN DOS FUENTES DE INFORMACIÓN:
        1. CONTEXTO GLOBAL: La lista completa de todos los episodios existentes hasta la fecha.
        2. FRAGMENTOS DE TRANSCRIPCIONES: Partes específicas del contenido donde se encuentra la respuesta detallada.

        INSTRUCCIONES:
        - Si el usuario pide LISTAR episodios, invitados, o temas generales, USA EL CONTEXTO GLOBAL.
        - Si el usuario pregunta sobre un tema específico (qué dijo tal persona, cómo funciona X), USA LOS FRAGMENTOS DE TRANSCRIPCIONES.
        - Si la respuesta no está en ninguna fuente, di que no tienes esa información.
        - Ordena cronológicamente si se pide (fíjate en el número de episodio #XX si existe).

        === CONTEXTO GLOBAL (LISTA DE TODOS LOS EPISODIOS) ===
        {global_episodes}
        ======================================================
        
        === FRAGMENTOS DE TRANSCRIPCIONES RELEVANTES ===
        {context_text}
        ================================================

        Pregunta: {query}
        
        Respuesta:
        """
        
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error generando respuesta con Gemini: {e}")
        return "Lo siento, hubo un error al procesar tu solicitud con la IA."
