"""
CRUD APPOINTMENT
"""
from aplicacion.forms.appointment.appointment_create import AppointmentForm
# pyrefly: ignore [missing-import]
from flask import (Blueprint,flash,render_template,url_for,redirect,request)
from aplicacion.forms.appointment.appointment_update import AppointmentUpdate
from aplicacion.appointment.appointment_model import AppointmentModel
from aplicacion.db import get_db
from aplicacion.services.google_calendar import CalendarService

bp = Blueprint('appointment',__name__)

@bp.route('/appointment_create', methods=['GET', 'POST'])
def appointment_create():
    """DOC"""
    appointment_form = AppointmentForm()
    db,c = get_db()
    c.execute('select pet_id, pet_names,pet_tutor_name from vetki.pet_data order by pet_names asc')
    mascotas = c.fetchall()
    c.execute("SELECT pet_id, pet_names FROM vetki.pet_data ORDER BY pet_names ASC")

    if appointment_form.validate_on_submit():
        sql = """
            INSERT INTO vetki.appointments (pet_id, appointment_date)
            VALUES (%s, %s)
        """
        valores = (
            appointment_form.appointment_pet.data, 
            appointment_form.appointment_date.data, 
        )
        c.execute(sql, valores)
        db.commit()
        # --- ENVÍO A GOOGLE CALENDAR ---
        appointment_data = appointment_form.appointment_pet.data
        appointment_name = dict(appointment_form.appointment_pet.choices).get(appointment_data, 'Paciente Desconocido')
        try:
            calendario = CalendarService()
            link_evento = calendario.create_event(appointment_name , appointment_form.appointment_date.data)
            if link_evento:
                print(link_evento)
                flash("¡Cita agendada y sincronizada en Google Calendar!", "success")
            else:
                flash("Cita guardada, pero Google Calendar rechazó la solicitud.", "warning")
        except Exception as e:
            print(f"Error Calendario: {e}")
            flash("Cita guardada, pero hubo un error de configuración en Google Calendar.", "warning")
            
        return redirect(url_for('index.index'))

    return render_template('appointment/appointment_create.html', appointment_form=appointment_form, mascotas=mascotas)
@bp.route("/appointment_read", methods = ['GET','POST'])
def appointment_read():
    """Lista de pet"""
    db, c = get_db()
    c.execute('''
        SELECT a.appointment_id, a.appointment_date, p.pet_names, p.pet_id 
        FROM vetki.appointments a
        JOIN vetki.pet_data p ON a.pet_id = p.pet_id
        ORDER BY a.appointment_date ASC
    ''')
    datos_crudos = c.fetchall()
    # Usamos el modelo para limpiar los datos
    objetos_cita = [AppointmentModel(d) for d in datos_crudos]
    
    return render_template('appointment/appointment_read.html', citas=objetos_cita)
@bp.route("/appointment_update/<int:appointment_id>", methods=['GET','POST'])
def appointment_update(appointment_id):
    """Modifica la cita (appointment)
        Dividido en 3 bloques
        - Preparacion
        - MOSTRAR DATOS
        - POST
    """
    form_update = AppointmentUpdate()
    db, cursor = get_db()
    # 1. Traer datos de la cita
    cursor.execute('SELECT * FROM vetki.appointments WHERE appointment_id = %s', (appointment_id,))
    appointment_data = cursor.fetchone()
    if not appointment_data:
        flash("La cita solicitada no existe.", "error")
        return redirect(url_for('appointment.appointment_read'))
    # 2. Llenar el select de mascotas
    cursor.execute('SELECT pet_id, pet_names FROM vetki.pet_data ORDER BY pet_names ASC')
    pet_data = cursor.fetchall()
    form_update.appointment_pet.choices = [(valor['pet_id'], valor['pet_names']) for valor in pet_data]
    # POST - Validación
    if form_update.validate_on_submit():
        appointment_pet = form_update.appointment_pet.data
        appointment_date = form_update.appointment_date.data
        data = (appointment_pet, appointment_date, appointment_id)
        sql = """
            UPDATE vetki.appointments
            SET pet_id = %s, appointment_date = %s
            WHERE appointment_id = %s
        """
        try:
            cursor.execute(sql, data)
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
        form_update.appointment_pet.data = appointment_data['pet_id']
        form_update.appointment_date.data = appointment_data['appointment_date']
    return render_template("appointment/appointment_update.html", appointment_update=form_update, pet_data=pet_data)
@bp.route("/appointment_delete/<int:appointment_id>",methods = ['GET','POST'])
def appointment_delete(appointment_id):
    """Elimina PET"""
    if not appointment_id:
        flash("No existe la cita", "error")
    db,c = get_db()
    c.execute("delete from appointments where appointment_id = %s",(appointment_id,))
    db.commit()
    return(redirect(url_for('appointment.appointment_read')))