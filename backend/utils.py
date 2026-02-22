"""
Utilidades y helpers para la aplicación
"""
import logging
import os
from functools import wraps
from flask import session, redirect, url_for, jsonify
import json


def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Configura un logger personalizado
    
    Args:
        name: Nombre del logger
        log_file: Ruta del archivo de log (opcional)
        level: Nivel de logging
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (opcional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def login_required(f):
    """
    Decorador para proteger rutas que requieren autenticación
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('vista_login'))
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """
    Decorador para proteger endpoints API que requieren autenticación
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'error': 'Unauthorized', 'message': 'Usuario no autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function


def load_json_file(file_path: str, default=None):
    """
    Carga un archivo JSON de forma segura
    
    Args:
        file_path: Ruta al archivo JSON
        default: Valor por defecto si hay error o no existe
        
    Returns:
        Contenido del JSON o default
    """
    if default is None:
        default = []
    
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error decodificando JSON {file_path}: {e}")
        return default
    except Exception as e:
        logging.error(f"Error cargando archivo {file_path}: {e}")
        return default


def save_json_file(file_path: str, data, indent: int = 2) -> bool:
    """
    Guarda datos en un archivo JSON de forma segura
    
    Args:
        file_path: Ruta al archivo JSON
        data: Datos a guardar
        indent: Espacios de indentación
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error guardando archivo {file_path}: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo eliminando caracteres no seguros
    
    Args:
        filename: Nombre del archivo original
        
    Returns:
        Nombre de archivo sanitizado
    """
    import re
    # Eliminar caracteres no alfanuméricos excepto .-_
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Reemplazar espacios por guiones bajos
    filename = re.sub(r'\s+', '_', filename)
    return filename


def validate_image_extension(filename: str) -> bool:
    """
    Valida que la extensión del archivo sea una imagen válida
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        True si es una extensión válida, False en caso contrario
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_directories(*dirs):
    """
    Crea múltiples directorios si no existen
    
    Args:
        *dirs: Rutas de directorios a crear
    """
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
