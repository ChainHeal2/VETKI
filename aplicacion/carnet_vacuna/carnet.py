"""
CARNET DE VACUNACION-VETKI
"""
from flask import (Blueprint,flash,render_template, session,url_for,redirect,request)
from aplicacion.db import get_db
from aplicacion.carnet_vacuna.CarnetModel import CarnetModel

bp = Blueprint('carnet',__name__,)

@bp.route("/carnet_read/<int:pet_id>", methods=['GET'])
def carnet_read(pet_id):
    """Devuelve el carnet de vacunas de la mascota con paginación."""
    _, c = get_db()
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = 5

    c.execute(
        "SELECT COUNT(*) AS total FROM vetki.vaccinations WHERE pet_id = %s",
        (pet_id,),
    )
    count_result = c.fetchone()
    total_records = count_result['total'] if count_result else 0
    total_pages = max((total_records + per_page - 1) // per_page, 1)
    page = min(page, total_pages)
    offset = (page - 1) * per_page

    consulta =("""
            SELECT 
            -- Datos de la mascota y tutor (Tabla pet_data)
            p.pet_id,
            p.pet_names AS pet_name,
            p.pet_species_name AS species,
            p.pet_race AS breed,
            p.pet_datebirth AS datebirth,
            p.pet_gender AS gender,
            p.pet_reproductive_status AS reproductive_status,
            p.pet_tutor_name AS tutor_name,
            p.pet_tutor_phone AS tutor_phone,
            p.pet_tutor_address AS tutor_address,
            -- Datos de las vacunas (Tabla vetki.vaccinations)
            v.id AS vaccine_id,
            v.vaccine_name,
            v.application_date,
            v.lot_number,
            v.veterinarian_notes
            FROM vetki.pet_data p
            LEFT JOIN vetki.vaccinations v ON p.pet_id = v.pet_id
            WHERE p.pet_id = %s
            ORDER BY v.application_date DESC, v.id DESC
            LIMIT %s OFFSET %s;""")
    c.execute(consulta, (pet_id, per_page, offset))
    carnet = CarnetModel(c.fetchall())
    return render_template(
        'carnet/carnet_read.html',
        carnet=carnet,
        page=page,
        total_pages=total_pages,
        total_records=total_records,
    )
