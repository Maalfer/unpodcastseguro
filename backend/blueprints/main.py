"""
Blueprint Principal
Maneja rutas públicas principales: home, políticas, sitemap, robots
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, make_response, current_app
from datetime import datetime
from backend.config import Config
from backend.utils import load_json_file

main_bp = Blueprint('main', __name__)


@main_bp.route("/", methods=["GET", "POST"])
def vista_home():
    """Vista de la página principal"""
    if request.method == "POST":
        correo = request.form.get("correo")
        if correo:
            ruta_archivo = os.path.join(Config.STATIC_FOLDER, "correos.txt")
            try:
                os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
                with open(ruta_archivo, "a", encoding="utf-8") as f:
                    f.write(correo + "\n")
                flash("Gracias por suscribirte a la newsletter.", "success")
            except Exception as e:
                flash(f"Error al guardar el correo: {e}", "danger")
        return redirect(url_for("main.vista_home"))
    
    # Cargar datos desde JSON files
    guests = load_json_file(Config.GUESTS_JSON, default=[])
    colaboradores = load_json_file(Config.COLABORADORES_JSON, default=[])
    newsletters = load_json_file(Config.NEWSLETTERS_JSON, default=[])
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
        "home.html", 
        guests=guests, 
        colaboradores=colaboradores, 
        newsletters=newsletters, 
        fundadores=fundadores, 
        estadisticas=estadisticas, 
        hero_subtitle=hero_subtitle, 
        about_data=about_data
    )


@main_bp.route('/buscador')
def vista_buscador():
    """Vista del buscador de episodios"""
    return render_template('buscador.html')


@main_bp.route("/politica-privacidad")
def politica_privacidad():
    """Política de privacidad"""
    return render_template("politicas/politica_privacidad.html")


@main_bp.route("/aviso-legal")
def aviso_legal():
    """Aviso legal"""
    return render_template("politicas/aviso_legal.html")


@main_bp.route("/cookies")
def cookies():
    """Política de cookies"""
    return render_template("politicas/cookies.html")


@main_bp.route('/robots.txt')
def robots_txt():
    """Archivo robots.txt para SEO"""
    return send_from_directory(current_app.static_folder, 'robots.txt', mimetype='text/plain')


@main_bp.route('/sitemap.xml')
def sitemap_xml():
    """Sitemap XML para SEO"""
    pages = [
        {
            'loc': 'https://unpodcastseguro.com/',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '1.0'
        },
        {
            'loc': 'https://unpodcastseguro.com/buscador',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        },
        {
            'loc': 'https://unpodcastseguro.com/politica-privacidad',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.3'
        },
        {
            'loc': 'https://unpodcastseguro.com/aviso-legal',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.3'
        }
    ]
    
    sitemap_xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for page in pages:
        sitemap_xml_content += '  <url>\n'
        sitemap_xml_content += f'    <loc>{page["loc"]}</loc>\n'
        sitemap_xml_content += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        sitemap_xml_content += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        sitemap_xml_content += f'    <priority>{page["priority"]}</priority>\n'
        sitemap_xml_content += '  </url>\n'
    
    sitemap_xml_content += '</urlset>'
    
    response = make_response(sitemap_xml_content)
    response.headers['Content-Type'] = 'application/xml'
    return response


@main_bp.app_errorhandler(404)
def page_not_found(e):
    """Manejador global para error 404"""
    return render_template('404.html'), 404


@main_bp.app_errorhandler(403)
def forbidden_access(e):
    """Manejador global para error 403"""
    return render_template('403.html'), 403
