"""Servicio para la gestión de vacunas y citas asociadas."""
from datetime import date, datetime, time, timedelta
from aplicacion.db import get_db


def fetch_pet_vaccinations(pet_id):
    """Consulta el historial de vacunas de una mascota."""
    db, cursor = get_db()
    cursor.execute(
        "SELECT id, vaccine_name, application_date, next_due_date, lot_number, "
        "veterinarian_notes FROM vetki.vaccinations WHERE pet_id = %s "
        "ORDER BY application_date DESC",
        (pet_id,),
    )
    rows = cursor.fetchall()
    return [
        {
            **row,
            "application_date": row["application_date"].isoformat(),
            "next_due_date": row["next_due_date"].isoformat() if row["next_due_date"] else None,
        }
        for row in rows
    ]


def register_vaccination(pet_id, vaccine_name, application_date, next_due_date=None, lot_number=None, notes=None):
    """Inserta la vacuna en BD y genera el borrador de cita de refuerzo."""
    db, cursor = get_db()
    cursor.execute(
        "INSERT INTO vetki.vaccinations "
        "(pet_id, vaccine_name, application_date, next_due_date, lot_number, veterinarian_notes) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (pet_id, vaccine_name, application_date, next_due_date, lot_number, notes),
    )
    vaccination_id = cursor.fetchone()["id"]

    if next_due_date:
        cursor.execute(
            "SELECT 1 FROM vetki.appointments WHERE pet_id = %s "
            "AND appointment_date::date = %s LIMIT 1",
            (pet_id, next_due_date),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO vetki.appointments "
                "(appointment_google_event_id, pet_id, appointment_date) "
                "VALUES (%s, %s, %s)",
                (
                    "vaccination-draft",
                    pet_id,
                    datetime.combine(next_due_date, time(9, 0)),
                ),
            )
    db.commit()
    return vaccination_id


def fetch_upcoming_vaccination_alerts(days_ahead=7):
    """Retorna las vacunas próximas a vencer."""
    db, cursor = get_db()
    target = date.today() + timedelta(days=days_ahead)
    cursor.execute(
        "SELECT v.id, v.pet_id, p.pet_names, v.vaccine_name, v.next_due_date "
        "FROM vetki.vaccinations v JOIN vetki.pet_data p ON p.pet_id = v.pet_id "
        "WHERE v.next_due_date = %s ORDER BY v.id",
        (target,),
    )
    return cursor.fetchall()