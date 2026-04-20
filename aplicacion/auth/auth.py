"""Módulo de Autenticación Central"""
import functools
from flask import (Blueprint, flash, g, render_template, request, url_for, session, redirect)
from werkzeug.security import check_password_hash
from aplicacion.db import get_db
from aplicacion.forms.user.user_form import UserForm
from werkzeug.security import generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/user_register', methods=['GET', 'POST'])
def user_register():
    """Página Pública Inicial de Registro"""
    user_form = UserForm()
    session.clear()
    if user_form.validate_on_submit():
        user_rut = user_form.user_rut.data
        user_email = user_form.user_email.data
        user_names = user_form.user_names.data
        user_surnames = user_form.user_surnames.data
        user_password = user_form.user_password.data
        
        hashed_pw = generate_password_hash(user_password)
        db, cursor = get_db()
        sql = """
            INSERT INTO vetki.user_data (user_rut, user_email, user_names, user_surnames, user_password) 
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(sql, (user_rut, user_email, user_names, user_surnames, hashed_pw))
            db.commit()
            flash("Personal registrado de forma exitosa. Inicia Sesión para entrar al Mando Clínico.", "success")
            return redirect(url_for('auth.user_login'))
        except Exception as e:
            db.rollback()
            flash(f"Error al registrar usuario: es posible que el correo o RUT ya existan ({e})", "danger")
    elif request.method == 'POST':
        flash("Revisa los errores de validación del formulario", "danger")
    return render_template('auth/register.html', user_form=user_form)


@bp.route('/user_login', methods=['GET', 'POST'])
def user_login():
    """Inicio de Sesión Oficial usando Correo Electrónico"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db, cursor = get_db()
        error = None
        cursor.execute('SELECT * FROM vetki.user_data WHERE user_email = %s', (email,))
        user_row = cursor.fetchone()
        if user_row is None:
            error = 'Correo electrónico no registrado o contraseña inválida.'
        elif not check_password_hash(user_row['user_password'], password):
            error = 'Correo electrónico no registrado o contraseña inválida.'
        if error is None:
            session.clear()
            session['user_id'] = user_row['user_id']
            session['username'] = f"{user_row['user_names']} {user_row['user_surnames'] or ''}".strip()
            flash("Conectado exitosamente.", "success")
            return redirect(url_for('pet.index'))
        flash(error, "danger")
    return render_template('auth/login.html')

@bp.route('/user_logout')
def user_logout():
    """Destruye la sesión actual"""
    session.clear()
    flash("Has cerrado tu sesión.", "success")
    return redirect(url_for('auth.user_login'))

@bp.before_app_request
def load_logged_in_user():
    """Carga los datos del usuario loggeado globalmente en g.user"""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db, cursor = get_db()
        cursor.execute('SELECT * FROM vetki.user_data WHERE user_id = %s', (user_id,))
        g.user = cursor.fetchone()

def login_required(view):
    """Decorador estricto para las vistas del dashboard"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.user_login'))
        return view(**kwargs)
    return wrapped_view