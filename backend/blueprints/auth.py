"""
Blueprint de Autenticación
Maneja login, logout y perfil de usuario
"""
import sqlite3
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login-unpodcastseguro', methods=['GET', 'POST'])
def vista_login():
    """Vista de inicio de sesión"""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(Config.DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username=?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password): 
            session['usuario'] = username
            return redirect(url_for('dashboard.vista_dashboard'))
        else:
            error = 'Credenciales incorrectas'
    return render_template('dashboard/login.html', error=error)


@auth_bp.route('/logout')
def vista_logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('auth.vista_login'))


@auth_bp.route('/perfil', methods=['GET', 'POST'])
def vista_perfil():
    """Vista de perfil de usuario"""
    if 'usuario' not in session:
        return redirect(url_for('auth.vista_login'))

    if request.method == 'POST':
        nuevo_usuario = request.form.get('nuevo_usuario')
        nueva_contrasena = request.form.get('nueva_contrasena')

        conn = sqlite3.connect(Config.DATABASE)
        cursor = conn.cursor()

        if nuevo_usuario:
            cursor.execute("UPDATE usuarios SET username = ? WHERE username = ?", 
                         (nuevo_usuario, session['usuario']))
            session['usuario'] = nuevo_usuario

        if nueva_contrasena:
            hash_nueva = generate_password_hash(nueva_contrasena)
            cursor.execute("UPDATE usuarios SET password = ? WHERE username = ?", 
                         (hash_nueva, session['usuario']))

        conn.commit()
        conn.close()
        flash('Datos actualizados correctamente', 'success')
        return redirect(url_for('auth.vista_perfil'))

    return render_template('dashboard/perfil.html', usuario=session['usuario'])
