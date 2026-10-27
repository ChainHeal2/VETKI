"""
CRUD APPOINTMENT
"""
from aplicacion.forms.appointment.appointment_form import AppointmentForm
# pyrefly: ignore [missing-import]
from flask import (Blueprint,flash,render_template, session,url_for,redirect,request,jsonify)
from aplicacion.blueprints.appointment.appointment_model import AppointmentModel
from aplicacion.blueprints.pet.pet_model import PetModel
from aplicacion.db import get_db,orm_db
from aplicacion.schema import appointments,pet_data
from sqlalchemy import insert,select,update
from datetime import datetime

import math

bp = Blueprint('appointment',__name__)

@bp.route('/appointment_create/<int:pet_id>', methods=['GET', 'POST'])
def appointment_create(pet_id):
    """Crea una cita en la BD interna usando orm_db.session."""
    appointment_form = AppointmentForm()
    # 1. PROCESAR Y GUARDAR LA CITA (POST)
    if appointment_form.validate_on_submit():
        try:
            # Construimos la sentencia INSERT
            stmt_insert = insert(appointments).values(
                pet_id=pet_id,
                appointment_date=appointment_form.date.data,
                appointment_reason=appointment_form.reason.data,
                appointment_end_date=(
                    appointment_form.end_date.data
                    if hasattr(appointment_form, 'end_date')
                    and appointment_form.end_date.data
                    else None
                ),
            )
            # Ejecutamos la inserción y confirmamos la transacción
            orm_db.session.execute(stmt_insert)
            orm_db.session.commit()

            flash('Cita agendada exitosamente.', 'success')
            return redirect(
                url_for('appointment.appointment_read')
            )  # Ajusta esta ruta a tu vista del calendario

        except Exception as e:
            orm_db.session.rollback()  # Si hay error, revertimos los cambios en la BD
            flash(f'Error al agendar la cita: {str(e)}', 'danger')

    # 2. CONSULTAR EL NOMBRE DE LA MASCOTA PARA MOSTRAR EN LA PLANTILLA (GET)
    stmt_pet = select(pet_data.c.pet_names).where(pet_data.c.pet_id == pet_id)
    pet_row = orm_db.session.execute(stmt_pet).fetchone()

    if not pet_row:
        flash('La mascota no existe.', 'warning')
        return redirect(
            url_for('main.index')
        )  # Ajusta a tu ruta principal/listado

    pet_name = pet_row.pet_names

    return render_template(
        'appointment/appointment_create.html',
        appointment_form=appointment_form,
        pet_name=pet_name,
    )
    
@bp.route('/appointment_read', methods=['GET'])
def appointment_read():
    return render_template('appointment/appointment_read.html')

@bp.route("/appointments_list", methods=['GET'])
def appointments_list():
    """Lista de citas médicas con soporte para búsqueda por paciente y paginación"""
   # Consulta SQL con JOIN para traer los datos de la cita y la mascota
    stmt = (
        select(
            appointments.c.appointment_id,
            appointments.c.appointment_reason,
            appointments.c.appointment_date,
            appointments.c.appointment_end_date,
            pet_data.c.pet_names,
            pet_data.c.pet_tutor_name,
            pet_data.c.pet_tutor_address,
        )
        .select_from(
            appointments.join(
                pet_data, 
                appointments.c.pet_id == pet_data.c.pet_id
            )
        )
    )

    results = orm_db.session.execute(stmt).mappings().all()

    # Formateamos los datos como lo requiere FullCalendar
    events = []
    for row in results:
        pet_name = row['pet_names'] or "Mascota"
        reason = row['appointment_reason'] or "Consulta"

        events.append({
            "id": row['appointment_id'],
            # Título que se mostrará en el bloque del calendario
            "title": f"🐾 {pet_name}: {reason}",
            # Las fechas deben ir en formato ISO 8601 string (ej: '2026-10-15T10:30:00')
            "start": row['appointment_date'].isoformat() if row['appointment_date'] else None,
            "end": row['appointment_end_date'].isoformat() if row['appointment_end_date'] else None,
            # URL usada por el modal para cargar el formulario de edición
            "url": f"/appointment_update/{row['appointment_id']}",
            # Propiedades extra por si quieres mostrar más datos en tooltips
            "extendedProps": {
                "tutor": row['pet_tutor_name'],
                "reason": reason,
                "petName": pet_name,
                "address": row['pet_tutor_address']
            }
        })

    return jsonify(events)

@bp.route("/appointment_move/<int:appointment_id>", methods=["POST"])
def appointment_move(appointment_id):
    """Guarda el nuevo horario de una cita movida desde el calendario."""
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify(error="Debes iniciar sesión para mover una cita."), 401

    payload = request.get_json(silent=True) or {}
    try:
        new_start = datetime.fromisoformat(payload.get("start", ""))
    except (TypeError, ValueError):
        return jsonify(error="La nueva fecha de la cita no es válida."), 400

    if new_start <= datetime.now():
        return jsonify(error="La cita debe quedar en una fecha futura."), 400

    # Solo se puede mover una cita asociada a una mascota del usuario actual.
    appointment = orm_db.session.execute(
        select(
            appointments.c.pet_id,
            appointments.c.appointment_date,
            appointments.c.appointment_end_date,
        )
        .select_from(
            appointments.join(
                pet_data, appointments.c.pet_id == pet_data.c.pet_id
            )
        )
        .where(
            appointments.c.appointment_id == appointment_id,
            pet_data.c.pet_user_id == user_id,
        )
    ).mappings().first()

    if appointment is None:
        return jsonify(error="La cita no existe o no tienes permiso para moverla."), 404

    # Mantiene la hora y duración de la cita al moverla a otro día.
    time_delta = new_start - appointment["appointment_date"]
    values = {"appointment_date": new_start}
    if appointment["appointment_end_date"] is not None:
        values["appointment_end_date"] = appointment["appointment_end_date"] + time_delta

    try:
        orm_db.session.execute(
            update(appointments)
            .where(appointments.c.appointment_id == appointment_id)
            .values(**values)
        )
        orm_db.session.commit()
    except Exception:
        orm_db.session.rollback()
        return jsonify(error="No se pudo guardar el nuevo horario."), 500

    return jsonify(message="Horario de la cita actualizado correctamente.")

@bp.route("/appointment_update/<int:appointment_id>", methods=['GET','POST'])
def appointment_update(appointment_id):
    """Modifica la cita (appointment) en la BD usando orm_db.session."""
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    user_id = session.get("user_id")
    if user_id is None:
        if is_ajax:
            return jsonify(error="Debes iniciar sesión para editar una cita."), 401
        return redirect(url_for("auth.user_login"))

    form_update = AppointmentForm()

    # Buscar únicamente citas asociadas a mascotas del usuario actual.
    stmt_appointment = select(
        appointments.c.appointment_id,
        appointments.c.pet_id,
        appointments.c.appointment_date,
        appointments.c.appointment_reason,
        appointments.c.appointment_end_date,
        pet_data.c.pet_names,
        pet_data.c.pet_tutor_name,
    ).select_from(
        appointments.join(pet_data, appointments.c.pet_id == pet_data.c.pet_id)
    ).where(
        appointments.c.appointment_id == appointment_id,
        pet_data.c.pet_user_id == user_id,
    )

    appointment_data = (
        orm_db.session.execute(stmt_appointment).mappings().fetchone()
    )

    if not appointment_data:
        if is_ajax:
            return jsonify(error="La cita no existe o no tienes permiso para editarla."), 404
        flash("La cita solicitada no existe.", "warning")
        return redirect(
            url_for('appointment.appointment_read')
        )  # Ajusta según tu vista

    pet_info = {
        "pet_id": appointment_data["pet_id"],
        "pet_names": appointment_data["pet_names"],
        "pet_tutor_name": appointment_data["pet_tutor_name"],
    }

    if form_update.validate_on_submit():
        if (
            form_update.end_date.data
            and form_update.end_date.data <= form_update.date.data
        ):
            message = "La fecha de término debe ser posterior al inicio."
            if is_ajax:
                return jsonify(error=message), 422
            flash(message, "warning")
        else:
            try:
                stmt_update = (
                    update(appointments)
                    .where(appointments.c.appointment_id == appointment_id)
                    .values(
                        appointment_date=form_update.date.data,
                        appointment_reason=form_update.reason.data,
                        appointment_end_date=form_update.end_date.data,
                    )
                )

                orm_db.session.execute(stmt_update)
                orm_db.session.commit()

                if is_ajax:
                    return jsonify(message="Cita actualizada correctamente.")
                flash("Cita actualizada correctamente.", "success")
                return redirect(url_for('appointment.appointment_read'))

            except Exception:
                orm_db.session.rollback()
                message = "Ocurrió un error al actualizar la cita."
                if is_ajax:
                    return jsonify(error=message), 500
                flash(message, "danger")

    elif request.method == 'POST' and is_ajax:
        errors = [error for field_errors in form_update.errors.values() for error in field_errors]
        return jsonify(error=" ".join(errors) or "Revisa los datos ingresados."), 422

    elif request.method == 'POST':
        flash("Error en el formulario. Por favor verifica los datos.", "warning")

    # Precargar datos en el formulario para la edición.
    if request.method == 'GET':
        form_update.date.data = appointment_data['appointment_date']
        form_update.reason.data = appointment_data['appointment_reason']
        form_update.end_date.data = appointment_data['appointment_end_date']

    if is_ajax and request.method == "GET":
        return render_template(
            "appointment/appointment_modal.html",
            appointment_update=form_update,
            appointment_data=appointment_data,
            pet_data=pet_info,
        )

    return render_template(
        "appointment/appointment_update.html",
        appointment_update=form_update,
        appointment_data=appointment_data,
        pet_data=pet_info,
    )

@bp.route("/appointment_delete/<int:appointment_id>",methods = ['GET','POST'])
def appointment_delete(appointment_id):
    """Elimina PET"""
    if not appointment_id:
        flash("No existe la cita", "error")
    db,c = get_db()
    c.execute("delete from appointments where appointment_id = %s",(appointment_id,))
    db.commit()
    return(redirect(url_for('appointment.appointment_read')))
