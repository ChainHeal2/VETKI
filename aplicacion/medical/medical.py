"""
CRUD-EXPEDIENTES CLINICOS
"""
from flask import (Blueprint,flash,render_template,url_for,redirect,request, session)
from aplicacion.auth.auth import login_required
from aplicacion.db import get_db
from aplicacion.forms.medical_records.medical_form import MedicalRecordForm
from aplicacion.medical.medical_model import MedicalRecordModel
from aplicacion.pet.pet_model import PetModel

bp = Blueprint('medical',__name__,url_prefix='/medical')

@bp.route("/medical_create/<int:pet_id>", methods = ['GET','POST'])
def medical_create(pet_id):
    """Crea un nuevo expediente clinico"""
    medical_record_form = MedicalRecordForm(prefix='medical_record')
    # el prefix es para diferenciar los campos del formulario en caso de tener varios formularios en la misma plantilla y nos ahorra escribir nombres largos en el HTML
    # los datos con prefix se veran de esta forma en el HTML: medical_record-fieldname
    db,cursor = get_db()
    cursor.execute('select * from pet_data where pet_id =%s',(pet_id,))
    pet_data = cursor.fetchone()
    if medical_record_form.validate_on_submit():
        date = medical_record_form.date.data
        reason = medical_record_form.reason.data
        weigth = medical_record_form.weigth.data
        temperature = medical_record_form.temperature.data
        heart = medical_record_form.heart.data
        respiratory = medical_record_form.respiratory.data
        water = medical_record_form.water.data
        capillary = medical_record_form.capillary.data
        arterial = medical_record_form.arterial.data
        history = medical_record_form.history.data
        signals = medical_record_form.signals.data
        diagnosis = medical_record_form.diagnosis.data
        tratment = medical_record_form.tratment.data
        pet_id = pet_data['pet_id']
        user_id = session.get('user_id')
        appointment_id = None
        
        data = (reason,weigth,temperature,
                heart,respiratory,water,
                capillary,arterial,date,
                history,signals,diagnosis,tratment,
                pet_id,user_id,appointment_id)
        sql = """
                INSERT INTO medical_records (medical_record_reason,medical_record_weight,medical_record_temperature,
                medical_record_heart,medical_record_respiratory,medical_record_water,
                medical_record_capillary,medical_record_arterial,medical_record_date,
                medical_record_medical_history,medical_record_signals,medical_record_diagnosis,medical_record_treatment,
                medical_record_pet_id,medical_record_user_id,medical_record_appointment_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
        cursor.execute(sql,data)
        flash("Expediente clinico creado correctamente", "success")
        db.commit()
        return redirect(url_for('medical.medical_read'))
    return render_template('medical_records/medical_create.html',medical_record_form = medical_record_form,mascota = pet_data)

@bp.route("/medical_read", methods = ['GET','POST'])
@login_required
def medical_read():
    """Lista de pet"""
    db,c = get_db()
    c.execute('select * from vw_pet_tutor where pet_user_id = %s', (session.get('user_id'),))
    datos = c.fetchall()
    medical_model_list = [PetModel(ficha) for ficha in datos]
    return render_template('medical_records/medical_read.html',tabla = medical_model_list)
@bp.route("/pet_history/<int:pet_id>", methods = ['GET','POST'])
def pet_history(pet_id):
    """Historial medico de una mascota
    consultamos los mas recientes primero
    """
    db,c = get_db()
    sql = """
        SELECT r.*,  p.pet_names, p.pet_species_name, p.pet_tutor_name 
        FROM medical_records r
        JOIN pet_data p ON r.medical_record_pet_id = p.pet_id
        WHERE r.medical_record_pet_id = %s
        ORDER BY r.medical_record_date DESC
    """
    c.execute(sql,(pet_id,))
    datos = c.fetchall()
    medical_model_list = [MedicalRecordModel(ficha) for ficha in datos]
    return render_template("medical_records/pet_history.html",tabla = medical_model_list,pet_id=pet_id)

@bp.route("/pet_delete/<int:pet_id>",methods = ['GET','POST'])
def pet_delete(pet_id):
    """Elimina PET"""
    error = None
    if not pet_id:
        error = "no hay pet"
        flash(error)
    db,c = get_db()
    c.execute("delete from pet_data where pet_id = %s",(pet_id,))
    db.commit()
    return(redirect(url_for('pet.pet_read')))