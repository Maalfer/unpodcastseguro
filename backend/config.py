"""
Configuración de la aplicación Flask
Contiene todas las rutas de archivos y configuraciones centralizadas
"""
import os

# Directorio base (raíz del proyecto, no backend/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Configuración de Flask
class Config:
    """Configuración base de la aplicación"""
    
    # Directorio base del proyecto
    BASE_DIR = BASE_DIR
    
    # Secret Key (Generated dynamically on startup)
    
    # AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Sesión
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to False for local development (HTTP)
    PERMANENT_SESSION_LIFETIME = 3600
    
    # Compresión
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'text/javascript'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    # Rutas de carpetas
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TRANSCRIPTS_FOLDER = os.path.join(BASE_DIR, 'database', 'transcripts')
    IMAGES_FOLDER = os.path.join(BASE_DIR, 'static/images')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    TEMPLATES_FOLDER = os.path.join(BASE_DIR, 'templates')
    
    # Rutas de archivos JSON de datos
    DATA_FOLDER = os.path.join(STATIC_FOLDER, 'data')
    EPISODIOS_JSON = os.path.join(DATA_FOLDER, 'episodios.json')
    GUESTS_JSON = os.path.join(DATA_FOLDER, 'guests.json')
    COLABORADORES_JSON = os.path.join(DATA_FOLDER, 'colaboradores.json')
    NEWSLETTERS_JSON = os.path.join(DATA_FOLDER, 'newsletters.json')
    FUNDADORES_JSON = os.path.join(DATA_FOLDER, 'fundadores.json')
    RECOMENDACIONES_JSON = os.path.join(DATA_FOLDER, 'recomendaciones.json')
    ESTADISTICAS_JSON = os.path.join(DATA_FOLDER, 'estadisticas.json')
    ABOUT_JSON = os.path.join(DATA_FOLDER, 'about.json')
    
    # Base de datos
    DATABASE = os.path.join(BASE_DIR, 'database', 'usuarios.db')
    
    # Sincronización
    SYNC_LOG_PATH = os.path.join(BASE_DIR, 'sync_log.json')
    
    # YouTube
    YOUTUBE_CHANNEL_ID = "UCt379PginS13-VJJKvNeGgQ"
    XDG_CACHE_HOME = "/var/www/unpodcastseguro/cache"


# Crear directorios si no existen
@staticmethod
def create_directories():
    """Crea los directorios necesarios si no existen"""
    dirs = [
        Config.UPLOAD_FOLDER,
        Config.TRANSCRIPTS_FOLDER,
        Config.IMAGES_FOLDER,
        Config.DATA_FOLDER
    ]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

# Hacer create_directories un método estático de la clase
Config.create_directories = create_directories
