"""
Blueprint de Episodios
Maneja la edición y eliminación de episodios
"""
import os
import json
from flask import Blueprint, request, jsonify, session, redirect, url_for
from backend.config import Config
from backend.utils import load_json_file, save_json_file

episodes_bp = Blueprint('episodes', __name__)


def require_login(f):
    """Decorador para requerir login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'error': 'No autorizado'}), 403
        return f(*args, **kwargs)
    return decorated_function


@episodes_bp.route('/editar_episodio/<int:index>', methods=['POST'])
@require_login
def editar_episodio(index):
    """Editar un episodio específico"""
    try:
        episodios = load_json_file(Config.EPISODIOS_JSON, default=[])
        data = request.get_json()

        if 0 <= index < len(episodios):
            episodios[index]['titulo'] = data['titulo']
            episodios[index]['fecha'] = data['fecha']
            episodios[index]['duracion'] = data['duracion']
            episodios[index]['descripcion'] = data['descripcion']
            episodios[index]['imagen'] = data['imagen']
            episodios[index]['enlace'] = data['enlace']

            if save_json_file(Config.EPISODIOS_JSON, episodios):
                return jsonify({"mensaje": "Episodio actualizado correctamente."})
            else:
                return jsonify({"error": "Error al guardar episodio."}), 500
        else:
            return jsonify({"error": "Índice fuera de rango."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@episodes_bp.route('/eliminar_episodio/<int:index>', methods=['POST'])
@require_login
def eliminar_episodio(index):
    """Eliminar un episodio"""
    try:
        episodios = load_json_file(Config.EPISODIOS_JSON, default=[])

        if index < 0 or index >= len(episodios):
            return jsonify({'error': 'Índice inválido'}), 400

        episodio = episodios.pop(index)

        # Eliminar imagen asociada si existe
        ruta_imagen = episodio.get('imagen')
        if ruta_imagen:
            nombre_imagen = os.path.basename(ruta_imagen)
            ruta_completa = os.path.join(Config.IMAGES_FOLDER, nombre_imagen)
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)

        if save_json_file(Config.EPISODIOS_JSON, episodios):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar cambios'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
