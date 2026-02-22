"""
Backend de la aplicación Un Podcast Seguro
Inicialización de Flask y configuración de blueprints
"""
import sys
import os
import glob
import secrets
import logging
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

# Configurar path para librerías locales
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
site_packages = glob.glob(os.path.join(parent_dir, 'librerias/lib/python*/site-packages'))
if site_packages:
    sys.path.insert(0, site_packages[0])

# Importar configuración y constantes
from backend.config import Config
from backend.constants import COMPRESS_MIMETYPES, COMPRESS_LEVEL, COMPRESS_MIN_SIZE, SECURITY_HEADERS


def create_app():
    """
    Factory function para crear la aplicación Flask
    
    Returns:
        Flask app configurada
    """
    app = Flask(__name__, 
                template_folder=os.path.join(parent_dir, 'templates'),
                static_folder=os.path.join(parent_dir, 'static'))
    
    # Cargar configuración
    configure_app(app)
    
    # Configurar logging
    setup_logging(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar hooks
    setup_hooks(app)
    
    # Crear directorios necesarios
    Config.create_directories()
    
    return app


def configure_app(app):
    """Configura la aplicación Flask"""
    
    # Secret key
    app.secret_key = secrets.token_hex(32)
    
    # Session configuration
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
    app.config['SESSION_COOKIE_SECURE'] = Config.SESSION_COOKIE_SECURE
    app.config['PERMANENT_SESSION_LIFETIME'] = Config.PERMANENT_SESSION_LIFETIME
    
    # Compression configuration
    app.config['COMPRESS_MIMETYPES'] = COMPRESS_MIMETYPES
    app.config['COMPRESS_LEVEL'] = COMPRESS_LEVEL
    app.config['COMPRESS_MIN_SIZE'] = COMPRESS_MIN_SIZE
    
    # Environment variables
    os.environ["XDG_CACHE_HOME"] = Config.XDG_CACHE_HOME


def setup_logging(app):
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    app.logger.setLevel(logging.INFO)


def register_blueprints(app):
    """Registra todos los blueprints de la aplicación"""
    from backend.blueprints.main import main_bp
    from backend.blueprints.auth import auth_bp
    from backend.blueprints.dashboard import dashboard_bp
    from backend.blueprints.api import api_bp
    from backend.blueprints.episodes import episodes_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(episodes_bp, url_prefix='/admin')


def setup_hooks(app):
    """Configura hooks de request/response"""
    from backend.db import init_db, csrf_protect, generate_csrf_token
    
    # Inicializar base de datos
    init_db()
    
    # Configurar CSRF protection
    app.before_request(csrf_protect)
    app.jinja_env.globals['csrf_token'] = generate_csrf_token
    
    @app.after_request
    def add_security_headers(response):
        """Agrega headers de seguridad y caché"""
        
        # Cache configuration
        if request.path.startswith('/static/'):
            # Cache static files for 1 year
            if any(request.path.endswith(ext) for ext in 
                   ['.css', '.js', '.webp', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf']):
                response.cache_control.max_age = 31536000
                response.cache_control.public = True
        elif request.path.endswith('.json') and '/api/' not in request.path:
            # Cache JSON files for 1 hour
            response.cache_control.max_age = 3600
            response.cache_control.public = True
        elif request.path.endswith('.html') or request.path == '/':
            # Don't cache HTML pages
            response.cache_control.no_cache = True
            response.cache_control.must_revalidate = True
        
        # Security headers
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        
        return response
    
    @app.context_processor
    def inject_now():
        """Inyecta datetime.now en todos los templates"""
        from datetime import datetime
        return {'now': datetime.now()}
