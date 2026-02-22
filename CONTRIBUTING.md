# Guía para Desarrolladores - Un Podcast Seguro

## 🚀 Comenzando

### Prerequisitos

- Python 3.8+
- pip
- virtualenv (recomendado)

### Instalación para Desarrollo

```bash
# Clonar repositorio
git clone <repo-url>
cd ups

# Crear entorno virtual
python -m venv venv
source venv/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Ejecutar en modo desarrollo
python run.py
```

## 📁 Arquitectura del Proyecto

### Estructura de Archivos

```
ups/
├── app.py                  # Aplicación Flask principal
├── config.py              # Configuración centralizada
├── constants.py           # Constantes de la aplicación
├── utils.py               # Utilidades y helpers
├── run.py                 # Script de arranque
│
├── static/
│   ├── css/              # Estilos
│   ├── js/               # JavaScript
│   ├── data/             # JSON de datos
│   └── images/           # Imágenes
│
└── templates/            # Templates Jinja2
```

### Módulos Principales

#### `config.py`
- Configuración centralizada
- Rutas de archivos y carpetas
- Settings de Flask

#### `constants.py`
- Constantes de la aplicación
- Mensajes de error/éxito
- Configuraciones estáticas

#### `utils.py`
- Funciones de utilidad
- Decoradores
- Helpers para JSON
- Validaciones

## 🔧 Configuración

### Variables de Entorno

Archivo `.env`:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=tu-clave-secreta
YOUTUBE_CHANNEL_ID=tu-channel-id
```

### Configuración de la Base de Datos

SQLite3 con estructura:
- `usuarios` - Gestión de usuarios
- `transcripciones` - Transcripciones de videos
- Full-Text Search (FTS5)

## 📝 Convenciones de Código

### Python Style Guide

Seguimos [PEP 8](https://pep8.org/):

```python
# ✅ Correcto
def obtener_usuarios():
    """Obtiene lista de usuarios de la BD"""
    return User.query.all()

# ❌ Incorrecto
def GetUsers():
    return User.query.all()
```

### Nombres de Variables

- **Archivos**: `snake_case.py`
- **Clases**: `PascalCase`
- **Funciones**: `snake_case()`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Variables**: `snake_case`

### Docstrings

```python
def procesar_imagen(imagen_path: str, max_size: tuple) -> bool:
    """
    Procesa y optimiza una imagen
    
    Args:
        imagen_path: Ruta a la imagen
        max_size: Tupla (width, height) tamaño máximo
        
    Returns:
        True si se procesó correctamente, False en caso contrario
        
    Raises:
        FileNotFoundError: Si la imagen no existe
        ValueError: Si el tamaño no es válido
    """
    pass
```

## 🔒 Seguridad

### Headers de Seguridad

Implementados automáticamente:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`

### CSRF Protection

Todas las rutas POST requieren token CSRF:

```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

### Autenticación

Usar decoradores:

```python
from utils import login_required, api_login_required

@app.route('/dashboard')
@login_required
def vista_dashboard():
    pass

@app.route('/api/save')
@api_login_required
def api_save():
    pass
```

## 🧪 Testing

### Ejecutar Tests

```bash
# TODO: Implementar tests
pytest tests/
```

### Estructura de Tests

```python
def test_load_json_file():
    """Test carga de archivos JSON"""
    data = load_json_file('test.json', default=[])
    assert isinstance(data, list)
```

## 📊 Logging

### Configurar Logger

```python
from utils import setup_logger

logger = setup_logger('mi_modulo', 'logs/mi_modulo.log')
logger.info("Iniciando proceso...")
logger.error("Error crítico", exc_info=True)
```

### Niveles de Log

- `DEBUG`: Información detallada
- `INFO`: Confirmaciones normales
- `WARNING`: Advertencias
- `ERROR`: Errores
- `CRITICAL`: Errores críticos

## 🎨 Frontend

### CSS

- **Global**: `static/css/style.css`
- **Home**: `static/css/home.css`
- **Variables CSS**: Usar custom properties

```css
:root {
  --primary-color: #02182F;
  --secondary-color: #4885EA;
}
```

### JavaScript

- Usar ES6+
- Módulos cuando sea posible
- Async/await para operaciones asíncronas

```javascript
// ✅ Correcto
async function loadData() {
  const response = await fetch('/api/data');
  const data = await response.json();
  return data;
}
```

## 🔄 Flujo de Trabajo Git

### Branches

- `main`: Producción
- `develop`: Desarrollo
- `feature/*`: Nuevas características
- `fix/*`: Correcciones

### Commits

Usar mensajes descriptivos:

```bash
git commit -m "feat: Agregar validación de imágenes"
git commit -m "fix: Corregir error en carga de JSON"
git commit -m "docs: Actualizar README"
```

Prefijos:
- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato, no código
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Tareas de mantenimiento

## 📦 Despliegue

### Producción

```bash
# 1. Actualizar código
git pull origin main

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Reiniciar servicio
systemctl restart unpodcastseguro
```

### Checklist Pre-Despliegue

- [ ] Tests pasando
- [ ] Logs limpios
- [ ] Variables de entorno configuradas
- [ ] Backup de DB
- [ ] Headers de seguridad activos

## 🐛 Debugging

### Logs

```bash
# Ver logs en tiempo real
tail -f app.log

# Buscar errores
grep -i error app.log
```

### Flask Debug Mode

Solo en desarrollo:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📚 Recursos

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [SQLite3](https://www.sqlite.org/docs.html)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'feat: Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Contacto

- **Equipo**: Un Podcast Seguro
- **Email**: contacto@unpodcastseguro.com
