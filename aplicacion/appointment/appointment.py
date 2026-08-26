"""
CRUD APPOINTMENT
"""
from aplicacion.forms.appointment.appointment_form import AppointmentForm
# pyrefly: ignore [missing-import]
from flask import (Blueprint,flash,render_template, session,url_for,redirect,request)
from aplicacion.appointment.appointment_model import AppointmentModel
from aplicacion.pet.pet_model import PetModel
from aplicacion.db import get_db
from aplicacion.services.google_calendar import CalendarService
import math

bp = Blueprint('appointment',__name__)

@bp.route('/appointment_create/<int:pet_id>', methods=['GET', 'POST'])
def appointment_create(pet_id):
    """Crea un Agendamiento en la BD y envia a Google Calendar"""
    appointment_form = AppointmentForm()
    db,c = get_db()
    c.execute('select pet_id, pet_names,pet_tutor_name from vetki.pet_data where pet_id = %s', (pet_id,))
    mascotas = c.fetchall()
    c.execute('select * from pet_data where pet_id = %s', (pet_id,))
    mascota = PetModel(c.fetchone())
    if appointment_form.validate_on_submit():
        sql = """
            INSERT INTO vetki.appointments ( appointment_google_event_id,pet_id, appointment_date)
            VALUES (%s, %s, %s)
        """
        # --- ENVÍO A GOOGLE CALENDAR ---
        try:
            calendario = CalendarService()
            link_evento = calendario.create_event(mascota.names , appointment_form.date.data)
            if link_evento:
                valores = (link_evento, pet_id, appointment_form.date.data)
                c.execute(sql, valores)
                db.commit()
                flash("¡Cita agendada y sincronizada en Google Calendar!", "success")
            else:
                flash("Cita guardada, pero Google Calendar rechazó la solicitud.", "warning")
        except Exception as e:
            flash("Cita guardada, pero hubo un error de configuración en Google Calendar.", "warning")
        return redirect(url_for('appointment.appointment_read'))
    return render_template('appointment/appointment_create.html', appointment_form=appointment_form, mascotas=mascotas)

@bp.route("/appointment_read", methods=['GET'])
def appointment_read():
    """Lista de citas médicas con soporte para búsqueda por paciente y paginación"""
    db, c = get_db()
    user_id = session.get('user_id')

    # Parámetros desde la URL
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    per_page = 6  # Número de citas por página
    offset = (page - 1) * per_page

    # 1. Obtener el total de registros para la paginación
    if search_query:
        count_sql = """
            SELECT COUNT(*) AS total 
            FROM vetki.appointments a
            JOIN vetki.pet_data p ON a.pet_id = p.pet_id
            WHERE p.pet_user_id = %s 
              AND (LOWER(p.pet_names) LIKE LOWER(%s) OR LOWER(p.pet_tutor_name) LIKE LOWER(%s))
        """
        term = f"%{search_query}%"
        c.execute(count_sql, (user_id, term, term))
    else:
        count_sql = """
            SELECT COUNT(*) AS total 
            FROM vetki.appointments a
            JOIN vetki.pet_data p ON a.pet_id = p.pet_id
            WHERE p.pet_user_id = %s
        """
        c.execute(count_sql, (user_id,))

    res_count = c.fetchone()
    total_records = res_count['total'] if res_count else 0
    total_pages = math.ceil(total_records / per_page) or 1

    # 2. Consulta de datos optimizada con columnas explícitas, LIMIT y OFFSET
    if search_query:
        sql = """
            SELECT a.appointment_id, a.appointment_date, p.pet_names, p.pet_id 
            FROM vetki.appointments a
            JOIN vetki.pet_data p ON a.pet_id = p.pet_id
            WHERE p.pet_user_id = %s 
              AND (LOWER(p.pet_names) LIKE LOWER(%s) OR LOWER(p.pet_tutor_name) LIKE LOWER(%s))
            ORDER BY a.appointment_date ASC
            LIMIT %s OFFSET %s
        """
        c.execute(sql, (user_id, term, term, per_page, offset))
    else:
        sql = """
            SELECT a.appointment_id, a.appointment_date, p.pet_names, p.pet_id 
            FROM vetki.appointments a
            JOIN vetki.pet_data p ON a.pet_id = p.pet_id
            WHERE p.pet_user_id = %s
            ORDER BY a.appointment_date ASC
            LIMIT %s OFFSET %s
        """
        c.execute(sql, (user_id, per_page, offset))

    datos_crudos = c.fetchall()
    objetos_cita = [AppointmentModel(d) for d in datos_crudos]

    return render_template(
        'appointment/appointment_read.html',
        citas=objetos_cita,
        search_query=search_query,
        page=page,
        total_pages=total_pages,
        total_records=total_records
    )

@bp.route("/appointment_update/<int:appointment_id>", methods=['GET','POST'])
def appointment_update(appointment_id):
    """Modifica la cita (appointment)
        Dividido en 3 bloques
        - Preparacion
        - MOSTRAR DATOS
        - POST
    """
    form_update = AppointmentForm()
    db, cursor = get_db()
    cursor.execute('SELECT * FROM vetki.appointments WHERE appointment_id = %s', (appointment_id,))
    #guardamos el cursor.fetchone() en una variable para poder usarla en el formulario
    appointment_data = cursor.fetchone()
    cursor.execute('SELECT pet_id, pet_names,pet_tutor_name FROM vetki.pet_data WHERE pet_id = %s', (appointment_data['pet_id'],))
    pet_data = cursor.fetchone()
    if not appointment_data:
        flash("La cita solicitada no existe.", "error")
        return redirect(url_for('appointment.appointment_read'))
    # POST - Validación
    if request.method == 'GET':
            #le envio los datos que puede modificar al formulario
            form_update.date = form_update['date']
            form_update.g_id.data = form_update['g_id']
    if form_update.validate_on_submit():
        appointment_date = form_update.date.data
        sql = """
            UPDATE vetki.appointments
            SET appointment_google_event_id = %s, appointment_date = %s
            WHERE appointment_id = %s
        """
        try:
            calendario = CalendarService()
            link_evento = calendario.update_event(appointment_data['appointment_google_event_id'], pet_data['pet_names'], appointment_date)
            data = (link_evento, appointment_date, appointment_id)
            cursor.execute(sql,data)
            db.commit()
            flash("¡Cita reprogramada exitosamente!", "success")
        except Exception as e:
            db.rollback()
            flash(f"Error al actualizar la cita: {e}", "error")
        return redirect(url_for('appointment.appointment_read'))
    elif request.method == 'POST':
        # Si falló la validación
        flash("Error en el formulario. Por favor verifica los datos.", "warning")
    # GET - Llenar formulario
    if request.method == 'GET':
        form_update.date.data = appointment_data['appointment_date']
    return render_template("appointment/appointment_update.html", appointment_update=form_update, appointment_data=appointment_data,pet_data=pet_data)

@bp.route("/appointment_delete/<int:appointment_id>",methods = ['GET','POST'])
def appointment_delete(appointment_id):
    """Elimina PET"""
    if not appointment_id:
        flash("No existe la cita", "error")
    db,c = get_db()
    c.execute("delete from appointments where appointment_id = %s",(appointment_id,))
    db.commit()
    return(redirect(url_for('appointment.appointment_read')))