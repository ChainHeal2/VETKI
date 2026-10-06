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
            pet_data.c.pet_tutor_name
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
            # Al hacer clic, redirigimos a la pantalla de edición
            "url": f"/appointment_update/{row['appointment_id']}",
            # Propiedades extra por si quieres mostrar más datos en tooltips
            "extendedProps": {
                "tutor": row['pet_tutor_name'],
                "reason": reason
            }
        })

    return jsonify(events)

@bp.route("/appointment_update/<int:appointment_id>", methods=['GET','POST'])
def appointment_update(appointment_id):
    """Modifica la cita (appointment) en la BD usando orm_db.session."""
    form_update = AppointmentForm()

    # 1. BLOQUE PREPARACIÓN / CONSULTA
    # Consultar la cita médica
    stmt_appointment = select(
        appointments.c.appointment_id,
        appointments.c.pet_id,
        appointments.c.appointment_date,
        appointments.c.appointment_reason,
        appointments.c.appointment_end_date,
    ).where(appointments.c.appointment_id == appointment_id)

    appointment_data = (
        orm_db.session.execute(stmt_appointment).mappings().fetchone()
    )

    if not appointment_data:
        flash("La cita solicitada no existe.", "warning")
        return redirect(
            url_for('appointment.appointment_read')
        )  # Ajusta según tu vista

    # Consultar los datos de la mascota
    stmt_pet = select(
        pet_data.c.pet_id, pet_data.c.pet_names, pet_data.c.pet_tutor_name
    ).where(pet_data.c.pet_id == appointment_data['pet_id'])

    pet_info = orm_db.session.execute(stmt_pet).mappings().fetchone()

    # 2. BLOQUE POST (Guardar cambios)
    if form_update.validate_on_submit():
        try:
            stmt_update = (
                update(appointments)
                .where(appointments.c.appointment_id == appointment_id)
                .values(
                    appointment_date=form_update.date.data,
                    appointment_reason=(
                        form_update.reason.data
                        if hasattr(form_update, 'reason')
                        else appointment_data['appointment_reason']
                    ),
                    appointment_end_date=(
                        form_update.end_date.data
                        if hasattr(form_update, 'end_date')
                        and form_update.end_date.data
                        else None
                    ),
                )
            )

            orm_db.session.execute(stmt_update)
            orm_db.session.commit()

            flash("Cita actualizada correctamente.", "success")
            return redirect(url_for('appointment.appointment_read'))

        except Exception as e:
            orm_db.session.rollback()
            flash(f"Error al actualizar la cita: {str(e)}", "danger")

    elif request.method == 'POST':
        flash(
            "Error en el formulario. Por favor verifica los datos.", "warning"
        )

    # 3. BLOQUE GET / MOSTRAR DATOS (Pre-llenar el formulario)
    if request.method == 'GET':
        form_update.date.data = appointment_data['appointment_date']

        if (
            hasattr(form_update, 'reason')
            and appointment_data['appointment_reason']
        ):
            form_update.reason.data = appointment_data['appointment_reason']

        if (
            hasattr(form_update, 'end_date')
            and appointment_data['appointment_end_date']
        ):
            form_update.end_date.data = appointment_data[
                'appointment_end_date'
            ]

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