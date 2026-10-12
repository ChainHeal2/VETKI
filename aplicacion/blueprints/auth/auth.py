"""Módulo de Autenticación, Usuarios y Permisos Central (Auth).

Maneja el registro, inicio de sesión, cierre de sesión, carga de usuario en contexto global
y decoradores de control de acceso para la plataforma clínica VETKI.
"""
import functools
import logging
from typing import Callable, Any
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
    Response
)
from werkzeug.security import check_password_hash, generate_password_hash
from aplicacion.db import get_db
from aplicacion.forms.user.user_form import UserForm

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/user_register', methods=['GET', 'POST'])
def user_register() -> str | Response:
    """Página pública y procesamiento del registro de nuevo personal médico."""
    if session.get('user_id'):
        return redirect(url_for('index.index'))

    user_form = UserForm()
    if user_form.validate_on_submit():
        user_rut = (user_form.user_rut.data or '').strip() or None
        user_email = user_form.user_email.data.strip().lower()
        user_names = user_form.user_names.data.strip()
        user_password = user_form.user_password.data

        hashed_pw = generate_password_hash(user_password)
        db, cursor = get_db()
        sql = """
            INSERT INTO vetki.user_data (user_rut, user_email, user_names, user_password, user_role) 
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(sql, (user_rut, user_email, user_names, hashed_pw, 'veterinario'))
            db.commit()
            flash("Personal registrado de forma exitosa. Inicia Sesión para entrar al Mando Clínico.", "success")
            session.clear()
            return redirect(url_for('auth.user_login'))
        except Exception as e:
            db.rollback()
            logger.error("Error al registrar nuevo usuario en base de datos: %s", e)
            flash("Error al registrar usuario: es posible que el correo o RUT ya se encuentren registrados en el sistema.", "danger")
    elif request.method == 'POST':
        flash("Revisa los errores de validación del formulario.", "danger")

    return render_template('auth/register.html', user_form=user_form)


@bp.route('/user_login', methods=['GET', 'POST'])
def user_login() -> str | Response:
    """Inicio de sesión oficial mediante credenciales (Correo electrónico y contraseña)."""
    if session.get('user_id'):
        return redirect(url_for('index.index'))

    if request.method == 'POST':
        email = (request.form.get('email') or request.form.get('user_email') or '').strip().lower()
        password = request.form.get('password') or request.form.get('user_password') or ''
        error = None

        if not email or not password:
            error = "Por favor, ingrese su correo electrónico y contraseña."
        else:
            try:
                db, cursor = get_db()
                sql = """
                    SELECT user_id, user_google_id, user_names, user_email, user_rut, user_password, user_role
                    FROM vetki.user_data
                    WHERE LOWER(user_email) = %s
                """
                cursor.execute(sql, (email,))
                user_row = cursor.fetchone()

                if user_row is None:
                    error = "Correo electrónico no registrado o contraseña inválida."
                elif not user_row.get('user_password'):
                    error = "Esta cuenta no cuenta con contraseña local asignada. Por favor, inicia sesión mediante Google."
                elif not check_password_hash(user_row['user_password'], password):
                    error = "Correo electrónico no registrado o contraseña inválida."
                else:
                    # Autenticación exitosa: regenerar sesión contra session fixation
                    session.clear()
                    session['user_id'] = user_row['user_id']
                    session['user_name'] = user_row['user_names']
                    session['user_email'] = user_row['user_email']
                    session['user_role'] = user_row.get('user_role') or 'veterinario'

                    flash("Conectado exitosamente.", "success")
                    next_url = request.args.get('next')
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect(url_for('index.index'))
            except Exception as e:
                logger.error("Error en consulta de inicio de sesión: %s", e)
                error = "Ocurrió un error al procesar el inicio de sesión. Por favor, reintente más tarde."

        if error:
            flash(error, "danger")

    return render_template('auth/login.html')


@bp.route('/user_logout', methods=['GET', 'POST'])
def user_logout() -> Response:
    """Cierra y destruye la sesión del usuario actual."""
    session.clear()
    flash("Has cerrado tu sesión.", "info")
    return redirect(url_for('auth.user_login'))


@bp.before_app_request
def load_logged_in_user() -> None:
    """Carga los datos del usuario logueado globalmente en g.user."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        try:
            db, cursor = get_db()
            cursor.execute(
                """
                SELECT user_id, user_google_id, user_names, user_email, user_rut, user_role
                FROM vetki.user_data
                WHERE user_id = %s
                """,
                (user_id,)
            )
            g.user = cursor.fetchone()
        except Exception as e:
            logger.error("Error al cargar usuario de sesión (user_id=%s): %s", user_id, e)
            g.user = None


def login_required(view: Callable) -> Callable:
    """Decorador estricto para proteger vistas del dashboard y rutas privadas."""
    @functools.wraps(view)
    def wrapped_view(*args: Any, **kwargs: Any) -> Any:
        if session.get('user_id') is None:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "No autorizado", "message": "Inicie sesión para acceder a este recurso."}), 401
            return redirect(url_for('auth.user_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def role_required(*allowed_roles: str) -> Callable:
    """Decorador para proteger vistas según rol de usuario (ej. 'admin', 'veterinario')."""
    def decorator(view: Callable) -> Callable:
        @functools.wraps(view)
        def wrapped_view(*args: Any, **kwargs: Any) -> Any:
            if session.get('user_id') is None:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({"error": "No autorizado"}), 401
                return redirect(url_for('auth.user_login', next=request.path))
            
            user_role = session.get('user_role', 'veterinario')
            if allowed_roles and user_role not in allowed_roles:
                flash("No tienes permisos suficientes para acceder a este apartado.", "warning")
                return redirect(url_for('index.index'))
            return view(*args, **kwargs)
        return wrapped_view
    return decorator