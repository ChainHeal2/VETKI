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
@login_required
def medical_create(pet_id):
    """Crea un nuevo expediente clinico"""
    medical_record_form = MedicalRecordForm(prefix='medical_record')
    # el prefix es para diferenciar los campos del formulario en caso de tener varios formularios en la misma plantilla y nos ahorra escribir nombres largos en el HTML
    # los datos con prefix se veran de esta forma en el HTML: medical_record-fieldname
    db,cursor = get_db()
    cursor.execute('select * from pet_data where pet_id =%s',(pet_id,))
    pet_data = cursor.fetchone()
    print(pet_data['pet_id'])
    if medical_record_form.validate_on_submit():
        print("Formulario válido")
        reason = medical_record_form.reason.data
        weigth = medical_record_form.weigth.data
        date = medical_record_form.date.data
        pet_id = pet_data['pet_id']
        user_id = session.get('user_id')
        appointment_id = None
        diagnosis = medical_record_form.diagnosis.data
        tratment = medical_record_form.tratment.data
        data = (reason,weigth,
                date,diagnosis,tratment,
                pet_id,user_id,appointment_id)
        print(data)
        sql = """
                INSERT INTO medical_records (medical_record_reason,medical_record_weight,medical_record_date,medical_record_diagnosis,medical_record_treatment,medical_record_pet_id,medical_record_user_id,medical_record_appointment_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """
        cursor.execute(sql,data)
        db.commit()
        return redirect(url_for('medical.medical_read'))
    print('Formulario no válido')
    return render_template('medical_records/medical_create.html',medical_record_form = medical_record_form,mascota = pet_data)

@bp.route("/medical_read", methods = ['GET','POST'])
@login_required
def medical_read():
    """Lista de pet"""
    db,c = get_db()
    c.execute('select * from medical_history where medical_record_user_id = %s', (session.get('user_id'),))
    datos = c.fetchall()
    medical_model_list = [MedicalRecordModel(ficha) for ficha in datos]
    return render_template('medical_records/medical_read.html',tabla = medical_model_list)
    
@bp.route("/medical_update_form/<int:medical_record_id>", methods = ['GET','POST'])
def medical_update_form(medical_record_id):
    """Modifica medical
        Dividido en 3 bloques
        - Preparacion
        - MOSTRAR DATOS
        - POST
    """
    pet_update = PetUpdate()
    db,cursor = get_db()

    cursor.execute('select * from pet_data where pet_id =%s',(pet_id,))
    pet_data = cursor.fetchone()

    cursor.execute('select pet_id,pet_species_name from pet_data where pet_id =%s',(pet_id,))
    pet_species_name = cursor.fetchone()
    
    if request.method == 'GET':
        pet_update.pet_names.data = pet_data['pet_names']
        pet_update.pet_species_name.data=pet_data['pet_species_name']
        pet_update.pet_race.data=pet_data['pet_race']
        pet_update.pet_datebirth.data=pet_data['pet_datebirth']
        pet_update.pet_microchip.data=pet_data['pet_microchip']
        pet_update.pet_gender.data=pet_data['pet_gender']
        pet_update.pet_color.data=pet_data['pet_color']
        pet_update.pet_rstatus.data=pet_data['pet_reproductive_status']
        pet_update.pet_tutor_name.data=pet_data['pet_tutor_name'].title()
        pet_update.pet_tutor_address.data=pet_data['pet_tutor_address']
        pet_update.pet_tutor_phone.data=pet_data['pet_tutor_phone']

    if pet_update.validate_on_submit():
        pet_user_id = session.get('user_id')
        pet_species_name = pet_update.pet_species_name.data
        pet_race = pet_update.pet_race.data
        pet_names = pet_update.pet_names.data
        pet_datebirth = pet_update.pet_datebirth.data
        pet_microchip = pet_update.pet_microchip.data
        pet_gender = pet_update.pet_gender.data
        pet_color = pet_update.pet_color.data
        pet_rstatus = pet_update.pet_rstatus.data
        pet_tutor_name = pet_update.pet_tutor_name.data
        pet_tutor_address = pet_update.pet_tutor_address.data
        pet_tutor_phone = pet_update.pet_tutor_phone.data
        data = (pet_user_id,pet_species_name,pet_names,pet_race,pet_datebirth,
                pet_microchip,pet_gender,pet_color,pet_rstatus,pet_tutor_name,pet_tutor_address,pet_tutor_phone,pet_id)
        sql = """
                UPDATE pet_data
                SET pet_user_id = %s, pet_species_name=%s, pet_names = %s, pet_race = %s, pet_datebirth = %s,
                pet_microchip = %s, pet_gender = %s, pet_color = %s, pet_reproductive_status = %s, pet_tutor_name = %s, pet_tutor_address = %s, pet_tutor_phone = %s
                WHERE pet_id = %s
                """
        cursor.execute(sql,data)
        db.commit()

        return redirect(url_for('pet.pet_read'))
    return render_template("pet/pet_update.html",pet_update = pet_update , pet_data = pet_data, pet_species_name=pet_species_name)

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