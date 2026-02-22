"""
Punto de entrada principal para Un Podcast Seguro
Servidor ASGI con Uvicorn + WhiteNoise
"""
import sys
import os
import glob
from datetime import datetime
import atexit

# Configurar path para librerías locales
base_dir = os.path.dirname(os.path.abspath(__file__))
site_packages = glob.glob(os.path.join(base_dir, 'librerias/lib/python*/site-packages'))
if site_packages:
    sys.path.insert(0, site_packages[0])

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from whitenoise import WhiteNoise
from apscheduler.schedulers.background import BackgroundScheduler

# Crear la aplicación usando el factory pattern
from backend import create_app

app = create_app()

# Wrap with WhiteNoise for static file serving
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/', max_age=31536000)

# Wrap the Flask app with WsgiToAsgi to make it ASGI compatible
asgi_app = WsgiToAsgi(app)


# ==================== SCHEDULER ====================

def run_sync():
    """Ejecutar sincronización de transcripciones"""
    try:
        from scripts import sync_transcripts
        sync_transcripts.sync_transcripts()
    except Exception as e:
        print(f"Error en sincronización automática: {e}")


# Configurar scheduler para sincronización automática
scheduler = BackgroundScheduler()
scheduler.add_job(func=run_sync, trigger="interval", hours=6, id='sync_job')
scheduler.add_job(func=run_sync, trigger="date", run_date=datetime.now(), id='startup_sync')
scheduler.start()

# Registrar shutdown del scheduler
atexit.register(lambda: scheduler.shutdown())

print("[INFO] Sincronización automática de transcripciones activada (cada 6 horas)")


# ==================== MAIN ====================

if __name__ == "__main__":
    uvicorn.run("run:asgi_app", host="0.0.0.0", port=5000, reload=True, reload_excludes=["static/*"])
