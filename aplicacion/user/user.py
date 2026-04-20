from flask import Blueprint, render_template, redirect, url_for, flash, request
from aplicacion.db import get_db
from aplicacion.forms.user.user_form import UserForm
from werkzeug.security import generate_password_hash

bp = Blueprint('user', __name__)

@bp.route('/user_create', methods=['GET', 'POST'])
def user_create():
    """Registra nuevo usuario"""
    user_form = UserForm()
    if user_form.validate_on_submit():
        user_rut = user_form.user_rut.data
        user_email = user_form.user_email.data
        user_names = user_form.user_names.data
        user_surnames = user_form.user_surnames.data
        user_password = user_form.user_password.data
        
        # Encriptación de contraseña
        hashed_pw = generate_password_hash(user_password)
        
        db, cursor = get_db()
        sql = """
            INSERT INTO vetki.user_data (user_rut, user_email, user_names, user_surnames, user_password) 
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(sql, (user_rut, user_email, user_names, user_surnames, hashed_pw))
            db.commit()
            flash("Usuario registrado exitosamente", "success")
            return redirect(url_for('pet.index'))
        except Exception as e:
            db.rollback()
            flash(f"Error al registrar usuario: verificando campos únicos {e}", "danger")
    elif request.method == 'POST':
        flash("Revisa los errores de validación del formulario", "danger")

    return render_template('user/user_create.html', user_form=user_form)

@bp.route('/user_read', methods=['GET'])
def user_read():
    """Muestra tabla de usuarios"""
    db, cursor = get_db()
    cursor.execute("SELECT user_id, user_rut, user_names, user_surnames FROM vetki.user_data ORDER BY user_id DESC")
    usuarios = cursor.fetchall()
    return render_template('user/user_read.html', usuarios=usuarios)

@bp.route('/user_update/<int:user_id>', methods=['GET', 'POST'])
def user_update(user_id):
    """Actualiza datos del usuario"""
    user_form = UserForm()
    db, cursor = get_db()
    
    # Optional password change logic (if empty, keep old password)
    # Removing password Required locally inside this method just for ease
    user_form.user_password.validators = [] 
    
    if user_form.validate_on_submit():
        user_rut = user_form.user_rut.data
        user_email = user_form.user_email.data
        user_names = user_form.user_names.data
        user_surnames = user_form.user_surnames.data
        new_password = user_form.user_password.data
        
        try:
            if new_password:
                hashed_pw = generate_password_hash(new_password)
                sql = "UPDATE vetki.user_data SET user_rut=%s, user_email=%s, user_names=%s, user_surnames=%s, user_password=%s WHERE user_id=%s"
                cursor.execute(sql, (user_rut, user_email, user_names, user_surnames, hashed_pw, user_id))
            else:
                sql = "UPDATE vetki.user_data SET user_rut=%s, user_email=%s, user_names=%s, user_surnames=%s WHERE user_id=%s"
                cursor.execute(sql, (user_rut, user_email, user_names, user_surnames, user_id))
            
            db.commit()
            flash("Usuario actualizado con éxito", "success")
            return redirect(url_for('user.user_read'))
        except Exception as e:
            db.rollback()
            flash(f"Falló la actualización: {e}", "danger")
            
    elif request.method == 'GET':
        cursor.execute("SELECT * FROM vetki.user_data WHERE user_id = %s", (user_id,))
        usr = cursor.fetchone()
        if usr:
            user_form.user_rut.data = usr['user_rut']
            user_form.user_email.data = usr['user_email']
            user_form.user_names.data = usr['user_names']
            user_form.user_surnames.data = usr['user_surnames']

    return render_template('user/user_update.html', user_update=user_form)

@bp.route('/user_delete/<int:user_id>')
def user_delete(user_id):
    db, cursor = get_db()
    cursor.execute("DELETE FROM vetki.user_data WHERE user_id = %s", (user_id,))
    db.commit()
    flash("Usuario destruido del sistema", "success")
    return redirect(url_for('user.user_read'))
