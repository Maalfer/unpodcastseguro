"""
Constantes de la aplicación
Centraliza todos los valores constantes para facilitar el mantenimiento
"""

# Extensiones de archivo permitidas
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'txt', 'md'}

# Tamaños máximos de archivo (en bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

# Configuración de caché
CACHE_STATIC_MAX_AGE = 31536000  # 1 año
CACHE_JSON_MAX_AGE = 3600  # 1 hora

# Configuración de sesión
SESSION_LIFETIME = 3600  # 1 hora

# Dimensiones de imágenes
IMAGE_THUMBNAIL_SIZE = (300, 300)
IMAGE_MAX_SIZE = (1920, 1080)

# YouTube
YOUTUBE_CHANNEL_ID = "UCt379PginS13-VJJKvNeGgQ"
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Mensajes de error
ERROR_MESSAGES = {
    'unauthorized': 'Usuario no autorizado',
    'invalid_file': 'Tipo de archivo no válido',
    'file_too_large': 'Archivo demasiado grande',
    'json_error': 'Error al procesar datos',
    'database_error': 'Error de base de datos',
    'not_found': 'Recurso no encontrado',
}

# Mensajes de éxito
SUCCESS_MESSAGES = {
    'saved': 'Guardado exitosamente',
    'deleted': 'Eliminado exitosamente',
    'updated': 'Actualizado exitosamente',
    'uploaded': 'Archivo subido exitosamente',
}

# Headers de seguridad
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'SAMEORIGIN',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
}

# Tipos MIME para compresión
COMPRESS_MIMETYPES = [
    'text/html',
    'text/css',
    'text/xml',
    'application/json',
    'application/javascript',
    'text/javascript',
]

# Nivel de compresión (1-9)
COMPRESS_LEVEL = 6

# Tamaño mínimo para comprimir (bytes)
COMPRESS_MIN_SIZE = 500
