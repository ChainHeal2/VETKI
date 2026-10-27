"""
CRUD-EXPEDIENTES CLINICOS
"""
from flask import (Blueprint, current_app, flash, render_template, url_for, redirect, request, session)
from aplicacion.db import get_db
from aplicacion.forms.medical_records.medical_form import MedicalRecordForm
from aplicacion.blueprints.medical.medical_model import MedicalRecordModel
from aplicacion.blueprints.pet.pet_model import PetModel
import math

bp = Blueprint('medical',__name__,url_prefix='/medical')


def _parse_service_price(service_id):
    """Lee el precio de un servicio como una cantidad entera de pesos CLP."""
    raw_price = request.form.get(f"service_price_{service_id}", "").strip()
    if not raw_price:
        return 0

    try:
        price = int(raw_price)
    except ValueError as error:
        raise ValueError("Ingresa precios enteros en pesos chilenos.") from error

    if price < 0:
        raise ValueError("Los precios deben ser números iguales o mayores que cero.")

    if price > 9_999_999_999:
        raise ValueError("El precio supera el máximo permitido.")

    return price


def _calculate_service_total(service_ids):
    """Suma los precios de los servicios seleccionados en el formulario."""
    return sum(_parse_service_price(service_id) for service_id in service_ids)


def _validate_displayed_total(total):
    """Comprueba que el total enviado por el formulario coincide con la suma."""
    try:
        displayed_total = int(request.form.get("medical_record_price", ""))
    except ValueError as error:
        raise ValueError("No se recibió un total válido para la ficha.") from error

    if displayed_total != total:
        raise ValueError("El total mostrado no coincide con los precios de los servicios.")


def _save_medical_record(cursor, db, form, pet_id, user_id, service_ids, total):
    """Guarda la ficha y sus servicios en una misma transacción."""
    sql = """
        INSERT INTO medical_records (
            medical_record_reason, medical_record_weight, medical_record_temperature,
            medical_record_heart, medical_record_respiratory, medical_record_water,
            medical_record_capillary, medical_record_arterial, medical_record_date,
            medical_record_medical_history, medical_record_signals,
            medical_record_diagnosis, medical_record_treatment,
            medical_record_pet_id, medical_record_user_id,
            medical_record_appointment_id, medical_record_price
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING medical_record_id
    """
    data = (
        form.reason.data,
        form.weigth.data,
        form.temperature.data,
        form.heart.data,
        form.respiratory.data,
        form.water.data,
        form.capillary.data,
        form.arterial.data,
        form.date.data,
        form.history.data,
        form.signals.data,
        form.diagnosis.data,
        form.tratment.data,
        pet_id,
        user_id,
        None,
        total,
    )

    try:
        cursor.execute(sql, data)
        medical_record_id = cursor.fetchone()["medical_record_id"]
        if service_ids:
            cursor.executemany(
                """INSERT INTO medical_record_services (medical_record_id, service_id)
                   VALUES (%s, %s)""",
                [(medical_record_id, service_id) for service_id in service_ids],
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

@bp.route("/medical_create/<int:pet_id>", methods = ['GET','POST'])
def medical_create(pet_id):
    """Crea un nuevo expediente clinico"""
    medical_record_form = MedicalRecordForm(prefix='medical_record')
    # el prefix es para diferenciar los campos del formulario en caso de tener varios formularios en la misma plantilla y nos ahorra escribir nombres largos en el HTML
    # los datos con prefix se veran de esta forma en el HTML: medical_record-fieldname
    db,cursor = get_db()
    cursor.execute(
        """SELECT pet_id, pet_names, pet_species_name
           FROM pet_data WHERE pet_id = %s""",
        (pet_id,),
    )
    pet_data = cursor.fetchone()
    cursor.execute(
        """SELECT service_id, service_name, service_category
           FROM services
           WHERE is_active = TRUE
           ORDER BY service_category, service_name"""
    )
    available_services = cursor.fetchall()
    medical_record_form.services.choices = [
        (service["service_id"], service["service_name"])
        for service in available_services
    ]
    service_groups = {}
    for service in available_services:
        service_groups.setdefault(service["service_category"], []).append(service)

    service_price_error = None
    if medical_record_form.validate_on_submit():
        selected_service_ids = medical_record_form.services.data or []
        try:
            total = _calculate_service_total(selected_service_ids)
            _validate_displayed_total(total)
        except ValueError as error:
            service_price_error = str(error)
        else:
            try:
                _save_medical_record(
                    cursor,
                    db,
                    medical_record_form,
                    pet_data["pet_id"],
                    session.get("user_id"),
                    selected_service_ids,
                    total,
                )
            except Exception:
                current_app.logger.exception("No se pudo guardar el expediente clínico")
                flash("Ocurrió un error al guardar el expediente. Revisa los datos e inténtalo nuevamente.", "error")
            else:
                flash("Expediente clínico creado correctamente", "success")
                return redirect(url_for('medical.medical_read'))

    return render_template(
        'medical_records/medical_create.html',
        medical_record_form=medical_record_form,
        mascota=pet_data,
        service_groups=service_groups,
        service_price_error=service_price_error,
    )

@bp.route("/medical_read", methods=['GET'])
def medical_read():
    """Lista de expedientes clínicos con soporte para búsqueda y paginación"""
    db, c = get_db()
    user_id = session.get('user_id')

    # Parámetros desde la URL
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    per_page = 8  # Cantidad de expedientes por página
    offset = (page - 1) * per_page

    # 1. Conteo total para paginación
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

    res_count = c.fetchone()
    total_records = res_count['total'] if res_count else 0
    total_pages = math.ceil(total_records / per_page) or 1

    # 2. Consulta proyectada (sin SELECT *) con LIMIT y OFFSET
    if search_query:
        sql = """
            SELECT 
                pet_id, pet_names, pet_species_name, 
                pet_datebirth, pet_tutor_name, pet_tutor_phone
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
                pet_id, pet_names, pet_species_name, 
                pet_datebirth, pet_tutor_name, pet_tutor_phone
            FROM pet_data 
            WHERE pet_user_id = %s 
            ORDER BY pet_names ASC
            LIMIT %s OFFSET %s
        """
        c.execute(sql, (user_id, per_page, offset))

    datos = c.fetchall()
    medical_model_list = [PetModel(ficha) for ficha in datos]

    return render_template(
        'medical_records/medical_read.html',
        tabla=medical_model_list,
        search_query=search_query,
        page=page,
        total_pages=total_pages,
        total_records=total_records
    )

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

    services_by_record = {}
    record_ids = [ficha["medical_record_id"] for ficha in datos]
    if record_ids:
        c.execute(
            """SELECT mrs.medical_record_id, s.service_name, s.service_category
               FROM medical_record_services mrs
               JOIN services s ON s.service_id = mrs.service_id
               WHERE mrs.medical_record_id = ANY(%s)
               ORDER BY s.service_category, s.service_name""",
            (record_ids,),
        )
        for service in c.fetchall():
            services_by_record.setdefault(service["medical_record_id"], []).append(
                {"name": service["service_name"], "category": service["service_category"]}
            )

    for record in medical_model_list:
        record.services = services_by_record.get(record.medical_id, [])

    return render_template(
        "medical_records/pet_history.html",
        tabla=medical_model_list,
        pet_id=pet_id,
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
