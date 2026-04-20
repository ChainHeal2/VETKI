"""
CRUD-MASCOTA
"""
from flask import (Blueprint,flash,render_template,url_for,redirect,request, session)
from aplicacion.auth.auth import login_required
from aplicacion.pet.pet_model import PetModel
from aplicacion.db import get_db
from aplicacion.forms.pet.pet_create import PetForm
from aplicacion.forms.pet.pet_update import PetUpdate

bp = Blueprint('pet',__name__,url_prefix='/pet')

@bp.route('/',methods = ['GET'])
def index():
    """Pagina de index"""
    return render_template('base.html')

@bp.route("/pet_create", methods = ['GET','POST'])
@login_required
def pet_create():
    """Crea un nueva pet"""
    pet_form = PetForm()
    db,cursor = get_db()
    cursor.execute('SELECT species_id, species_name FROM vetki.species_data')
    species_data = cursor.fetchall()
    pet_form.species_id.choices=[(valor['species_id'],
                                valor['species_name']) for valor  in species_data]

    if pet_form.validate_on_submit():
        pet_user_id = session.get('user_id')
        pet_species_id = pet_form.species_id.data
        pet_names = pet_form.pet_names.data
        pet_race = pet_form.pet_race.data
        pet_datebirth = pet_form.pet_datebirth.data
        pet_microchip = pet_form.pet_microchip.data
        pet_gender = pet_form.pet_gender.data
        pet_color = pet_form.pet_color.data
        pet_rstatus = pet_form.pet_rstatus.data
        data = (pet_user_id, pet_species_id,pet_names,pet_race,pet_datebirth,pet_microchip,pet_gender,pet_color,pet_rstatus)
        sql = """
            insert into pet_data(pet_user_id, pet_species_id,pet_names,pet_race,pet_datebirth,
            pet_microchip,pet_gender,pet_color,pet_reproductive_status)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql,data)
        db.commit()
        flash("Mascota ingresada con exito y asignada a su expediente!","success")
        return redirect(url_for('pet.pet_read'))
    return render_template('pet/pet_create.html',pet_form = pet_form)

@bp.route("/pet_read", methods = ['GET','POST'])
@login_required
def pet_read():
    """Lista de pet"""
    db,c = get_db()
    c.execute('select * from pet_data where pet_user_id = %s', (session.get('user_id'),))
    datos = c.fetchall()
    objetos_mascotas = [PetModel(f) for f in datos]
    return render_template('pet/pet_read.html',tabla = datos,mascotas = objetos_mascotas)
@bp.route("/pet_update_form/<int:pet_id>", methods = ['GET','POST'])
def pet_update_form(pet_id):
    """Modifica pets
        Dividido en 3 bloques
        - Preparacion
        - MOSTRAR DATOS
        - POST
    """
    pet_update = PetUpdate()
    db,cursor = get_db()

    cursor.execute('select * from pet_data where pet_id =%s',(pet_id,))
    pet_data = cursor.fetchone()

    cursor.execute('SELECT species_id, species_name FROM vetki.species_data')
    species_data = cursor.fetchall()

    pet_update.species_id.choices=[(valor['species_id'],valor['species_name']) for valor  in species_data]

    if request.method == 'GET':
        pet_update.pet_names.data = pet_data['pet_names']
        pet_update.species_id.data=pet_data['pet_species_id']
        pet_update.pet_race.data=pet_data['pet_race']
        pet_update.pet_datebirth.data=pet_data['pet_datebirth']
        pet_update.pet_microchip.data=pet_data['pet_microchip']
        pet_update.pet_gender.data=pet_data['pet_gender']
        pet_update.pet_color.data=pet_data['pet_color']
        pet_update.pet_rstatus.data=pet_data['pet_reproductive_status']
        
    if pet_update.validate_on_submit():
        pet_user_id = session.get('user_id')
        pet_species_id = pet_update.species_id.data
        pet_names = pet_update.pet_names.data.title()
        pet_race = pet_update.pet_race.data
        pet_datebirth = pet_update.pet_datebirth.data
        pet_microchip = pet_update.pet_microchip.data
        pet_gender = pet_update.pet_gender.data
        pet_color = pet_update.pet_color.data
        pet_rstatus = pet_update.pet_rstatus.data
        data = (pet_user_id, pet_species_id,pet_names,pet_race,pet_datebirth,
                pet_microchip,pet_gender,pet_color,pet_rstatus,pet_id)
        sql = """
                UPDATE pet_data
                SET pet_user_id = %s, pet_species_id = %s, pet_names = %s, pet_race = %s, pet_datebirth = %s,
                pet_microchip = %s, pet_gender = %s, pet_color = %s, pet_reproductive_status = %s
                WHERE pet_id = %s
                """
        cursor.execute(sql,data)
        db.commit()

        return redirect(url_for('pet.pet_read'))
    return render_template("pet/pet_update.html",pet_update = pet_update , pet_data = pet_data)

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