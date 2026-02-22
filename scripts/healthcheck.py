#!/usr/bin/env python3
"""
Health Check Script
Verifica el estado de la aplicación y sus dependencias
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

# Colores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_status(message, status='info'):
    """Imprime mensaje con color según el estado"""
    if status == 'success':
        print(f"{Colors.GREEN}✓{Colors.ENDC} {message}")
    elif status == 'warning':
        print(f"{Colors.YELLOW}⚠{Colors.ENDC} {message}")
    elif status == 'error':
        print(f"{Colors.RED}✗{Colors.ENDC} {message}")
    else:
        print(f"{Colors.BLUE}ℹ{Colors.ENDC} {message}")


def check_directories():
    """Verifica que los directorios necesarios existan"""
    print(f"\n{Colors.BOLD}Verificando directorios...{Colors.ENDC}")
    
    required_dirs = [
        'static',
        'static/css',
        'static/js',
        'static/data',
        'static/images',
        'templates',
        'uploads',
        'database',
        'database/transcripts'
    ]
    
    all_good = True
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    for relative_path in required_dirs:
        dir_path = os.path.join(base_dir, relative_path)
        if os.path.exists(dir_path):
            print_status(f"{relative_path}/", 'success')
        else:
            print_status(f"{relative_path}/ - NO EXISTE", 'error')
            all_good = False
    
    return all_good


def check_json_files():
    """Verifica que los archivos JSON sean válidos"""
    print(f"\n{Colors.BOLD}Verificando archivos JSON...{Colors.ENDC}")
    
    json_files = [
        'static/data/about.json',
        'static/data/colaboradores.json',
        'static/data/episodios.json',
        'static/data/estadisticas.json',
        'static/data/fundadores.json',
        'static/data/guests.json',
        'static/data/newsletters.json',
        'static/data/recomendaciones.json',
    ]
    
    all_good = True
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    for relative_file in json_files:
        json_file = os.path.join(base_dir, relative_file)
        if not os.path.exists(json_file):
            print_status(f"{relative_file} - NO EXISTE", 'warning')
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json.load(f)
            file_size = os.path.getsize(json_file)
            print_status(f"{relative_file} ({file_size} bytes)", 'success')
        except json.JSONDecodeError as e:
            print_status(f"{relative_file} - JSON INVÁLIDO: {e}", 'error')
            all_good = False
        except Exception as e:
            print_status(f"{relative_file} - ERROR: {e}", 'error')
            all_good = False
    
    return all_good


def check_database():
    """Verifica la conexión y estructura de la base de datos"""
    print(f"\n{Colors.BOLD}Verificando base de datos...{Colors.ENDC}")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(base_dir, 'database', 'usuarios.db')
    
    if not os.path.exists(db_path):
        print_status(f"Base de datos no existe en {db_path}", 'error')
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabla usuarios
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = cursor.fetchone()[0]
            print_status(f"Tabla 'usuarios' - {count} registros", 'success')
        else:
            print_status("Tabla 'usuarios' no existe", 'error')
            conn.close()
            return False
        
        # Verificar tabla transcripciones
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transcripciones'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM transcripciones")
            count = cursor.fetchone()[0]
            print_status(f"Tabla 'transcripciones' - {count} registros", 'success')
        else:
            print_status("Tabla 'transcripciones' no existe", 'warning')
        
        # Tamaño de la DB
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print_status(f"Tamaño de DB: {db_size:.2f} MB", 'info')
        
        conn.close()
        return True
        
    except Exception as e:
        print_status(f"Error conectando a DB: {e}", 'error')
        return False


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print(f"\n{Colors.BOLD}Verificando dependencias...{Colors.ENDC}")
    
    required_modules = [
        'flask',
        'PIL',
        'werkzeug',
        'apscheduler',
        'requests'
    ]
    
    all_good = True
    for module in required_modules:
        try:
            __import__(module)
            print_status(f"{module}", 'success')
        except ImportError:
            print_status(f"{module} - NO INSTALADO", 'error')
            all_good = False
    
    return all_good


def check_permissions():
    """Verifica permisos de escritura en directorios críticos"""
    print(f"\n{Colors.BOLD}Verificando permisos...{Colors.ENDC}")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Updated paths relative to base_dir
    write_dirs = [
        'uploads', 
        'static/data', 
        'database/transcripts'
    ]
    
    all_good = True
    for relative_path in write_dirs:
        dir_path = os.path.join(base_dir, relative_path)
        if os.path.exists(dir_path):
            if os.access(dir_path, os.W_OK):
                print_status(f"{relative_path}/ - escritura OK", 'success')
            else:
                print_status(f"{relative_path}/ - SIN permisos de escritura", 'error')
                all_good = False
        else:
            print_status(f"{relative_path}/ - no existe", 'warning')
    
    return all_good


def check_config_files():
    """Verifica archivos de configuración"""
    print(f"\n{Colors.BOLD}Verificando configuración...{Colors.ENDC}")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Secret key check removed as per user request
    pass
    
    if os.path.exists(os.path.join(base_dir, '.env')):
        print_status(".env encontrado", 'success')
    else:
        print_status(".env no existe (usando .env.example como referencia)", 'warning')
    
    return True


def main():
    """Ejecuta todas las verificaciones"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}  Health Check - Un Podcast Seguro{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.ENDC}\n")
    
    results = {
        'Directorios': check_directories(),
        'Archivos JSON': check_json_files(),
        'Base de Datos': check_database(),
        'Dependencias': check_dependencies(),
        'Permisos': check_permissions(),
        'Configuración': check_config_files(),
    }
    
    # Resumen
    print(f"\n{Colors.BOLD}{'='*50}{Colors.ENDC}")
    print(f"{Colors.BOLD}RESUMEN{Colors.ENDC}\n")
    
    all_passed = True
    for check, passed in results.items():
        if passed:
            print_status(f"{check}: OK", 'success')
        else:
            print_status(f"{check}: FALLÓ", 'error')
            all_passed = False
    
    print(f"{Colors.BOLD}{'='*50}{Colors.ENDC}\n")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Todos los checks pasaron correctamente{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Algunos checks fallaron{Colors.ENDC}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
