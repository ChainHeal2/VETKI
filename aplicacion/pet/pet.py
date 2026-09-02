"""
CRUD-MASCOTA
"""
from flask import (Blueprint,flash,render_template,url_for,redirect,request, session)
from aplicacion.auth.auth import login_required
from aplicacion.pet.pet_model import PetModel
from aplicacion.db import get_db
from aplicacion.forms.pet.pet_form import PetForm
import math

from aplicacion.utils import sanitizar

bp = Blueprint('pet',__name__,url_prefix='/pet')

@bp.route("/pet_create", methods = ['GET','POST'])
@login_required
def pet_create():
    """Crea una nueva pet"""
    pet_form = PetForm()
    db, cursor = get_db()

    if request.method == 'POST':
        if pet_form.validate_on_submit():
            # 1. Sanitizamos los datos del formulario
            form = sanitizar(pet_form.data)

            # 2. Armamos la tupla 'data' extrayendo directamente del diccionario sanitizado 'form'
            # (Garantiza el orden exacto para el SQL e ignora cosas extra como csrf_token)
            data = (
                session.get('user_id'),
                form.get('pet_species_name'),
                form.get('pet_names'),
                form.get('pet_race'),
                form.get('pet_datebirth'),  # Se mantiene la fecha intacta
                form.get('pet_microchip'),
                form.get('pet_gender'),
                form.get('pet_color'),
                form.get('pet_rstatus'),     # Se mapea con pet_reproductive_status en SQL
                form.get('pet_tutor_name'),
                form.get('pet_tutor_address'),
                form.get('pet_tutor_phone')
            )

            sql = """
                INSERT INTO vetki.pet_data (
                    pet_user_id, pet_species_name, pet_names, pet_race, pet_datebirth,
                    pet_microchip, pet_gender, pet_color, pet_reproductive_status,
                    pet_tutor_name, pet_tutor_address, pet_tutor_phone
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            # 3. Ejecutamos pasando 'data' en lugar de 'form.values()'
            cursor.execute(sql, data)
            db.commit()

            flash("Mascota ingresada con éxito y asignada a su expediente!", "success")
            return redirect(url_for('pet.pet_read'))
        else:
            for campo, lista_errores in pet_form.errors.items():
                # Extraemos el nombre visible del campo (ej: "Nombre de la mascota")
                etiqueta = getattr(pet_form, campo).label.text
                for error in lista_errores:
                    # Se envía directamente a la cola de flashes de Flask
                    flash(f"{etiqueta}: {error}", "error")

    return render_template('pet/pet_create.html', pet_form=pet_form)

@bp.route("/pet_read", methods=['GET'])
@login_required
def pet_read():
    """Lista de mascotas con soporte para búsqueda y paginación optimizada"""
    db, c = get_db()
    user_id = session.get('user_id')
    
    # Parámetros desde la URL
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    per_page = 6
    offset = (page - 1) * per_page

    # 1. Obtener el total de registros usando un ALIAS ("AS total")
    if search_query:
        count_sql = """
            SELECT COUNT(*) AS total 
            FROM pet_data 
            WHERE pet_user_id = %s 
              AND (LOWER(pet_names) LIKE LOWER(%s) OR LOWER(pet_tutor_name) LIKE LOWER(%s))
        """
        term = f"%{search_query}%"
        c.execute(count_sql, (user_id, term, term))
    else:
        count_sql = "SELECT COUNT(*) AS total FROM pet_data WHERE pet_user_id = %s"
        c.execute(count_sql, (user_id,))
    
    # 2. Acceso correcto al diccionario para RealDictCursor
    res_count = c.fetchone()
    total_records = res_count['total'] if res_count else 0
    total_pages = math.ceil(total_records / per_page) or 1

    # 3. Consulta de datos optimizada
    if search_query:
        sql = """
            SELECT 
                pet_id, pet_names, pet_species_name, pet_race, pet_datebirth,
                pet_microchip, pet_gender, pet_color, pet_reproductive_status,
                pet_tutor_name, pet_tutor_address, pet_tutor_phone
            FROM pet_data 
            WHERE pet_user_id = %s 
              AND (LOWER(pet_names) LIKE LOWER(%s) OR LOWER(pet_tutor_name) LIKE LOWER(%s))
            ORDER BY pet_names ASC
            LIMIT %s OFFSET %s
        """
        c.execute(sql, (user_id, term, term, per_page, offset))
    else:
        sql = """
            SELECT 
                pet_id, pet_names, pet_species_name, pet_race, pet_datebirth,
                pet_microchip, pet_gender, pet_color, pet_reproductive_status,
                pet_tutor_name, pet_tutor_address, pet_tutor_phone
            FROM pet_data 
            WHERE pet_user_id = %s 
            ORDER BY pet_names ASC
            LIMIT %s OFFSET %s
        """
        c.execute(sql, (user_id, per_page, offset))

    datos = c.fetchall()
    objetos_mascotas = [PetModel(f) for f in datos]

    return render_template(
        'pet/pet_read.html',
        tabla=datos,
        mascotas=objetos_mascotas,
        search_query=search_query,
        page=page,
        total_pages=total_pages,
        total_records=total_records
    )

@bp.route("/pet_update_form/<int:pet_id>", methods = ['GET','POST'])
def pet_update_form(pet_id):
    """Modifica pets
        Dividido en 3 bloques
        - Preparación
        - Carga de Datos (GET)
        - Procesamiento y Guardado (POST)
    """
    db, cursor = get_db()

    # 1. Traer datos actuales de la mascota (sirve para validar existencia y pasar a la plantilla)
    cursor.execute('SELECT * FROM vetki.pet_data WHERE pet_id = %s', (pet_id,))
    pet_data = cursor.fetchone()

    # Si la mascota no existe en BD, evitamos errores cargando un formulario vacío
    if not pet_data:
        flash("La mascota no fue encontrada.", "error")
        return redirect(url_for('pet.pet_read'))

    # Cargar formulario inicializándolo con los datos de la base de datos para el GET
    pet_update = PetForm(data=pet_data)
    # Ajuste manual solo para la variable con nombre distinto (pet_rstatus vs pet_reproductive_status)
    if request.method == 'GET':
        pet_update.pet_rstatus.data = pet_data.get('pet_reproductive_status')

    # 2. Procesamiento del POST cuando se envía el formulario
    if pet_update.validate_on_submit():
        # Sanitizamos los datos procesando el formulario completo de un solo golpe
        form = sanitizar(pet_update.data)

        # Mapeamos la tupla usando form.get() con los datos ya sanitizados (limpios)
        data = (
            session.get('user_id'),
            form.get('pet_species_name'),
            form.get('pet_names'),
            form.get('pet_race'),
            form.get('pet_datebirth'),
            form.get('pet_microchip'),
            form.get('pet_gender'),
            form.get('pet_color'),
            form.get('pet_rstatus'),       # Mapeado a pet_reproductive_status en SQL
            form.get('pet_tutor_name'),
            form.get('pet_tutor_address'),
            form.get('pet_tutor_phone'),
            pet_id                         # ID para la cláusula WHERE
        )

        sql = """
            UPDATE vetki.pet_data
            SET pet_user_id = %s,
                pet_species_name = %s,
                pet_names = %s,
                pet_race = %s,
                pet_datebirth = %s,
                pet_microchip = %s,
                pet_gender = %s,
                pet_color = %s,
                pet_reproductive_status = %s,
                pet_tutor_name = %s,
                pet_tutor_address = %s,
                pet_tutor_phone = %s
            WHERE pet_id = %s
        """

        cursor.execute(sql, data)
        db.commit()

        flash("Mascota actualizada con éxito!", "success")
        return redirect(url_for('pet.pet_read'))
    else:
        for campo, lista_errores in pet_update.errors.items():
            # Extraemos el nombre visible del campo (ej: "Nombre de la mascota")
            etiqueta = getattr(pet_update, campo).label.text
            for error in lista_errores:
                # Se envía directamente a la cola de flashes de Flask
                flash(f"{etiqueta}: {error}", "error")
    return render_template(
        "pet/pet_update.html",
        pet_update=pet_update,
        pet_data=pet_data
    )

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