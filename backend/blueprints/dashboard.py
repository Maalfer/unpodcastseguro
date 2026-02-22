"""
Blueprint de Dashboard
Maneja el panel de administración
"""
import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from PIL import Image
from backend.config import Config
from backend.utils import load_json_file, save_json_file

dashboard_bp = Blueprint('dashboard', __name__)


def require_login(f):
    """Decorador para requerir login en rutas del dashboard"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('auth.vista_login'))
        return f(*args, **kwargs)
    return decorated_function


@dashboard_bp.route('/')
@require_login
def vista_dashboard():
    """Vista principal del dashboard administrativo"""
    guests = load_json_file(Config.GUESTS_JSON, default=[])
    colaboradores = load_json_file(Config.COLABORADORES_JSON, default=[])
    newsletters = load_json_file(Config.NEWSLETTERS_JSON, default=[])
    recomendaciones = load_json_file(Config.RECOMENDACIONES_JSON, default=[])
    estadisticas = load_json_file(Config.ESTADISTICAS_JSON, default=[])
    about_data = load_json_file(Config.ABOUT_JSON, default={"paragraphs": [], "award": {}})
    
    # Procesar fundadores
    fundadores = []
    hero_subtitle = ""
    fundadores_data = load_json_file(Config.FUNDADORES_JSON, default=[])
    if isinstance(fundadores_data, dict):
        fundadores = fundadores_data.get('founders', [])
        hero_subtitle = fundadores_data.get('hero_subtitle', '')
    else:
        fundadores = fundadores_data

    return render_template(
        'dashboard/dashboard.html', 
        guests=guests, 
        colaboradores=colaboradores, 
        newsletters=newsletters, 
        fundadores=fundadores, 
        recomendaciones=recomendaciones, 
        estadisticas=estadisticas, 
        hero_subtitle=hero_subtitle, 
        about_data=about_data
    )


# ==================== GUESTS ====================

def get_next_image_number():
    """Obtiene el siguiente número para imagen de invitado"""
    invitados_dir = os.path.join(Config.IMAGES_FOLDER, 'invitados')
    if not os.path.exists(invitados_dir):
        os.makedirs(invitados_dir)
    
    files = os.listdir(invitados_dir)
    numbers = []
    for f in files:
        if f.endswith('.webp') or f.endswith('.png'):
            try:
                num = int(os.path.splitext(f)[0])
                numbers.append(num)
            except ValueError:
                pass
    
    return 1 if not numbers else max(numbers) + 1


@dashboard_bp.route('/api/save_guests', methods=['POST'])
@require_login
def api_save_guests():
    """Guardar lista de invitados"""
    try:
        new_guests = request.get_json()
        if save_json_file(Config.GUESTS_JSON, new_guests):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/upload_guest_image', methods=['POST'])
@require_login
def api_upload_guest_image():
    """Subir imagen de invitado"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    old_filename = request.form.get('old_filename')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            next_num = get_next_image_number()
            new_filename = f"{next_num}.webp"
            invitados_dir = os.path.join(Config.IMAGES_FOLDER, 'invitados')
            
            if not os.path.exists(invitados_dir):
                os.makedirs(invitados_dir)

            save_path = os.path.join(invitados_dir, new_filename)
            
            image = Image.open(file)
            image.save(save_path, 'WEBP', quality=85)
            
            # Eliminar imagen anterior si existe
            if old_filename and old_filename != 'logo.png' and 'invitados/' in old_filename:
                old_file_path = os.path.join(Config.IMAGES_FOLDER, old_filename)
                if os.path.exists(old_file_path) and os.path.isfile(old_file_path):
                    if os.path.abspath(old_file_path).startswith(os.path.abspath(invitados_dir)):
                        try:
                            os.remove(old_file_path)
                        except Exception as e:
                            print(f"Error deleting old image: {e}")

            return jsonify({'success': True, 'filepath': f"invitados/{new_filename}"})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# ==================== COLLABORATORS ====================

def get_next_collaborator_image_number():
    """Obtiene el siguiente número para imagen de colaborador"""
    colaboradores_dir = os.path.join(Config.IMAGES_FOLDER, 'colaboradores')
    if not os.path.exists(colaboradores_dir):
        os.makedirs(colaboradores_dir)
    
    files = os.listdir(colaboradores_dir)
    numbers = []
    for f in files:
        if f.endswith('.webp') or f.endswith('.png'):
            try:
                num = int(os.path.splitext(f)[0])
                numbers.append(num)
            except ValueError:
                pass
    
    return 1 if not numbers else max(numbers) + 1


@dashboard_bp.route('/api/save_collaborators', methods=['POST'])
@require_login
def api_save_collaborators():
    """Guardar lista de colaboradores"""
    try:
        new_data = request.get_json()
        if save_json_file(Config.COLABORADORES_JSON, new_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/upload_collaborator_image', methods=['POST'])
@require_login
def api_upload_collaborator_image():
    """Subir imagen de colaborador"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    old_filename = request.form.get('old_filename')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            next_num = get_next_collaborator_image_number()
            new_filename = f"{next_num}.webp"
            colaboradores_dir = os.path.join(Config.IMAGES_FOLDER, 'colaboradores')
            
            if not os.path.exists(colaboradores_dir):
                os.makedirs(colaboradores_dir)

            save_path = os.path.join(colaboradores_dir, new_filename)
            
            image = Image.open(file)
            image.save(save_path, 'WEBP', quality=85)
            
            # Eliminar imagen anterior
            if old_filename and 'colaboradores/' in old_filename:
                old_file_path = os.path.join(Config.IMAGES_FOLDER, old_filename)
                if os.path.exists(old_file_path) and os.path.isfile(old_file_path):
                    if os.path.abspath(old_file_path).startswith(os.path.abspath(colaboradores_dir)):
                        try:
                            os.remove(old_file_path)
                        except Exception as e:
                            print(f"Error deleting old image: {e}")

            return jsonify({'success': True, 'filepath': f"colaboradores/{new_filename}"})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# ==================== FOUNDERS ====================

def get_next_founder_image_number():
    """Obtiene el siguiente número para imagen de fundador"""
    fundadores_dir = os.path.join(Config.IMAGES_FOLDER, 'fundadores')
    if not os.path.exists(fundadores_dir):
        os.makedirs(fundadores_dir)
    
    files = os.listdir(fundadores_dir)
    numbers = []
    for f in files:
        if f.endswith('.webp') or f.endswith('.png'):
            try:
                num = int(os.path.splitext(f)[0])
                numbers.append(num)
            except ValueError:
                pass
    
    return 1 if not numbers else max(numbers) + 1


@dashboard_bp.route('/api/save_founders', methods=['POST'])
@require_login
def api_save_founders():
    """Guardar lista de fundadores"""
    try:
        new_data = request.get_json()
        if save_json_file(Config.FUNDADORES_JSON, new_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/upload_founder_image', methods=['POST'])
@require_login
def api_upload_founder_image():
    """Subir imagen de fundador"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    old_filename = request.form.get('old_filename')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            next_num = get_next_founder_image_number()
            new_filename = f"{next_num}.webp"
            fundadores_dir = os.path.join(Config.IMAGES_FOLDER, 'fundadores')
            
            if not os.path.exists(fundadores_dir):
                os.makedirs(fundadores_dir)

            save_path = os.path.join(fundadores_dir, new_filename)
            
            image = Image.open(file)
            image.save(save_path, 'WEBP', quality=85)
            
            # Eliminar imagen anterior
            if old_filename and 'fundadores/' in old_filename:
                old_file_path = os.path.join(Config.IMAGES_FOLDER, old_filename)
                if os.path.exists(old_file_path) and os.path.isfile(old_file_path):
                    if os.path.abspath(old_file_path).startswith(os.path.abspath(fundadores_dir)):
                        try:
                            os.remove(old_file_path)
                        except Exception as e:
                            print(f"Error deleting old image: {e}")

            return jsonify({'success': True, 'filepath': f"fundadores/{new_filename}"})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# ==================== OTHER DATA ====================

@dashboard_bp.route('/api/save_newsletters', methods=['POST'])
@require_login
def api_save_newsletters():
    """Guardar newsletters"""
    try:
        updated_newsletters = request.json
        if not isinstance(updated_newsletters, list):
            return jsonify({'error': 'Invalid format, expected a list'}), 400

        if save_json_file(Config.NEWSLETTERS_JSON, updated_newsletters):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/save_recommendations', methods=['POST'])
@require_login
def api_save_recommendations():
    """Guardar recomendaciones"""
    try:
        new_data = request.get_json()
        if save_json_file(Config.RECOMENDACIONES_JSON, new_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/save_stats', methods=['POST'])
@require_login
def api_save_stats():
    """Guardar estadísticas"""
    try:
        new_data = request.get_json()
        if save_json_file(Config.ESTADISTICAS_JSON, new_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/save_about', methods=['POST'])
@require_login
def api_save_about():
    """Guardar información 'Acerca de'"""
    try:
        new_data = request.get_json()
        if save_json_file(Config.ABOUT_JSON, new_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
