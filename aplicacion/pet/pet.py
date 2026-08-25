"""
CRUD-MASCOTA
"""
from flask import (Blueprint,flash,render_template,url_for,redirect,request, session)
from aplicacion.auth.auth import login_required
from aplicacion.pet.pet_model import PetModel
from aplicacion.db import get_db
from aplicacion.forms.pet.pet_create import PetForm

bp = Blueprint('pet',__name__,url_prefix='/pet')

@bp.route("/pet_create", methods = ['GET','POST'])
@login_required
def pet_create():
    """Crea un nueva pet"""
    pet_form = PetForm()
    db,cursor = get_db()

    if pet_form.validate_on_submit():
        pet_user_id = session.get('user_id')
        pet_species_name = pet_form.pet_species_name.data
        pet_names = pet_form.pet_names.data.lower()
        pet_race = pet_form.pet_race.data.lower()
        pet_datebirth = pet_form.pet_datebirth.data
        pet_microchip = pet_form.pet_microchip.data
        pet_gender = pet_form.pet_gender.data
        pet_color = pet_form.pet_color.data.lower()
        pet_rstatus = pet_form.pet_rstatus.data
        pet_tutor_name = pet_form.pet_tutor_name.data.lower()
        pet_tutor_address = pet_form.pet_tutor_address.data.lower()
        pet_tutor_phone = pet_form.pet_tutor_phone.data
        data = (pet_user_id, pet_species_name,pet_names,pet_race,pet_datebirth,pet_microchip,pet_gender,pet_color,pet_rstatus,pet_tutor_name,pet_tutor_address,pet_tutor_phone)
        sql = """
            insert into vetki.pet_data(pet_user_id, pet_species_name,pet_names,pet_race,pet_datebirth,
            pet_microchip,pet_gender,pet_color,pet_reproductive_status,pet_tutor_name,pet_tutor_address,pet_tutor_phone)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql,data)
        db.commit()
        flash("Mascota ingresada con exito y asignada a su expediente!","success")
        return redirect(url_for('pet.pet_read'))
    return render_template('pet/pet_create.html',pet_form = pet_form)

@bp.route("/pet_read", methods=['GET', 'POST'])
@login_required
def pet_read():
    """Lista de mascotas con soporte para búsqueda"""
    db, c = get_db()
    
    # Captura el texto ingresado en la barra de búsqueda (si existe)
    search_query = request.args.get('q', '').strip()
    user_id = session.get('user_id')

    if search_query:
        # Busca por nombre de la mascota o por el tutor coincidente
        sql = """
            SELECT * FROM pet_data 
            WHERE pet_user_id = %s 
              AND (LOWER(pet_names) LIKE LOWER(%s) OR LOWER(pet_tutor_name) LIKE LOWER(%s))
            ORDER BY pet_names ASC
        """
        term = f"%{search_query}%"
        c.execute(sql, (user_id, term, term))
    else:
        # Si no hay término de búsqueda, lista todas las mascotas del usuario
        sql = """
            SELECT * FROM pet_data 
            WHERE pet_user_id = %s 
            ORDER BY pet_names ASC
        """
        c.execute(sql, (user_id,))

    datos = c.fetchall()
    objetos_mascotas = [PetModel(f) for f in datos]

    return render_template(
        'pet/pet_read.html',
        tabla=datos,
        mascotas=objetos_mascotas,
        search_query=search_query
    )

@bp.route("/pet_update_form/<int:pet_id>", methods = ['GET','POST'])
def pet_update_form(pet_id):
    """Modifica pets
        Dividido en 3 bloques
        - Preparacion
        - MOSTRAR DATOS
        - POST
    """
    pet_update = PetForm()
    #pet update es el formulario que se va a mostrar en la vista, y que se va a validar cuando se haga submit
    db,cursor = get_db()

    cursor.execute('select * from pet_data where pet_id =%s',(pet_id,))
    pet_data = cursor.fetchone()

    cursor.execute('select pet_id,pet_species_name from pet_data where pet_id =%s',(pet_id,))
    pet_species_name = cursor.fetchone()
    
    if request.method == 'GET':
        #le envio los datos que puede modificar al formulario
        pet_update.pet_names.data = pet_data['pet_names']
        pet_update.pet_species_name.data=pet_data['pet_species_name']
        pet_update.pet_race.data=pet_data['pet_race']
        pet_update.pet_datebirth.data=pet_data['pet_datebirth']
        pet_update.pet_microchip.data=pet_data['pet_microchip']
        pet_update.pet_gender.data=pet_data['pet_gender']
        pet_update.pet_color.data=pet_data['pet_color']
        pet_update.pet_rstatus.data=pet_data['pet_reproductive_status']
        pet_update.pet_tutor_name.data=pet_data['pet_tutor_name']
        pet_update.pet_tutor_address.data=pet_data['pet_tutor_address']
        pet_update.pet_tutor_phone.data=pet_data['pet_tutor_phone']

    if pet_update.validate_on_submit():
        #cuando validate_on_submit es True, que es como lo definimos el formulario,ahivan los datos y validaciones
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
        #data es una tupla con los datos que se van a actualizar en la base de datos
        data = (pet_user_id,pet_species_name,pet_names.lower(),pet_race.lower(),pet_datebirth,
                pet_microchip,pet_gender,pet_color.lower(),pet_rstatus,pet_tutor_name.lower(),pet_tutor_address.lower(),pet_tutor_phone,pet_id)
        #creamos el script sql para actualizar los datos de la mascota en la base de datos
        sql = """
                UPDATE pet_data
                SET pet_user_id = %s, pet_species_name=%s, pet_names = %s, pet_race = %s, pet_datebirth = %s,
                pet_microchip = %s, pet_gender = %s, pet_color = %s, pet_reproductive_status = %s, pet_tutor_name = %s, pet_tutor_address = %s, pet_tutor_phone = %s
                WHERE pet_id = %s
                """
        cursor.execute(sql,data)
        db.commit()
        return redirect(url_for('pet.pet_read'))# nos redirecciona a la vista de lectura de mascotas
    return render_template("pet/pet_update.html",pet_update = pet_update , pet_data = pet_data, pet_species_name=pet_species_name)
    #al enviar el html, le enviamos el formulario que se va a mostrar en la vista, y los datos de la mascota que se van a mostrar en la vista
    #pet data es la tupla con los datos de la mascota
    

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