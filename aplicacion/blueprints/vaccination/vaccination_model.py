"""Modelo y operaciones de base de datos para las vacunas."""

from aplicacion.db import get_db


class VaccinationModel:
    """Representa una vacuna y centraliza sus operaciones CRUD."""

    def __init__(self, data):
        self.id = data.get("id")
        self.pet_id = data.get("pet_id")
        self.vaccine_name = data.get("vaccine_name")
        self.application_date = data.get("application_date")
        self.lot_number = data.get("lot_number")
        self.veterinarian_notes = data.get("veterinarian_notes")

    def to_dict(self):
        """Convierte el modelo a un diccionario que Flask puede devolver como JSON."""
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "vaccine_name": self.vaccine_name,
            "application_date": (
                self.application_date.isoformat() if self.application_date else None
            ),
            "lot_number": self.lot_number,
            "veterinarian_notes": self.veterinarian_notes,
        }

    @classmethod
    def get_by_pet(cls, pet_id):
        """Devuelve las vacunas de una mascota, de la más reciente a la más antigua."""
        _, cursor = get_db()
        cursor.execute(
            "SELECT id, pet_id, vaccine_name, application_date, lot_number, "
            "veterinarian_notes FROM vetki.vaccinations "
            "WHERE pet_id = %s ORDER BY application_date DESC, id DESC",
            (pet_id,),
        )
        return [cls(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_id(cls, pet_id, vaccination_id):
        """Busca una vacuna específica dentro de la mascota indicada."""
        _, cursor = get_db()
        cursor.execute(
            "SELECT id, pet_id, vaccine_name, application_date, lot_number, "
            "veterinarian_notes FROM vetki.vaccinations "
            "WHERE pet_id = %s AND id = %s",
            (pet_id, vaccination_id),
        )
        row = cursor.fetchone()
        return cls(row) if row else None

    @classmethod
    def create(cls, pet_id, data):
        """Guarda una vacuna nueva y devuelve su identificador."""
        db, cursor = get_db()
        try:
            cursor.execute(
                "INSERT INTO vetki.vaccinations "
                "(pet_id, vaccine_name, application_date, lot_number, veterinarian_notes) "
                "VALUES (%s, %s, CURRENT_DATE, %s, %s) RETURNING id",
                (
                    pet_id,
                    data["vaccine_name"],
                    data["lot_number"],
                    data["veterinarian_notes"],
                ),
            )
            vaccination_id = cursor.fetchone()["id"]
            db.commit()
            return vaccination_id
        except Exception:
            db.rollback()
            raise

    def update(self, data):
        """Actualiza los campos de esta vacuna."""
        db, cursor = get_db()
        try:
            cursor.execute(
                "UPDATE vetki.vaccinations SET vaccine_name = %s, "
                "lot_number = %s, veterinarian_notes = %s "
                "WHERE pet_id = %s AND id = %s RETURNING id",
                (
                    data["vaccine_name"],
                    data["lot_number"],
                    data["veterinarian_notes"],
                    self.pet_id,
                    self.id,
                ),
            )
            updated = cursor.fetchone() is not None
            db.commit()
            return updated
        except Exception:
            db.rollback()
            raise

    def delete(self):
        """Elimina esta vacuna de la base de datos."""
        db, cursor = get_db()
        try:
            cursor.execute(
                "DELETE FROM vetki.vaccinations "
                "WHERE pet_id = %s AND id = %s RETURNING id",
                (self.pet_id, self.id),
            )
            deleted = cursor.fetchone() is not None
            db.commit()
            return deleted
        except Exception:
            db.rollback()
            raise
