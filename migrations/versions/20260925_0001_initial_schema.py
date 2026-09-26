"""Crea el esquema inicial de VETKI.

Revision ID: 20260925_0001
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = "20260925_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA vetki")

    op.create_table(
        "user_data",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_google_id", sa.String(length=255), nullable=True),
        sa.Column("user_names", sa.String(length=40), nullable=False),
        sa.Column("user_email", sa.String(length=100), nullable=True),
        sa.Column("user_rut", sa.String(length=20), nullable=True),
        sa.Column("user_password", sa.String(length=255), nullable=True),
        sa.Column(
            "user_role", sa.String(length=20),
            server_default=sa.text("'veterinario'"), nullable=True,
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("user_google_id", name="user_data_user_google_id_key"),
        schema="vetki",
    )

    op.create_table(
        "pet_data",
        sa.Column("pet_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pet_user_id", sa.Integer(), nullable=True),
        sa.Column("pet_species_name", sa.String(length=50), nullable=True),
        sa.Column("pet_names", sa.String(length=100), nullable=False),
        sa.Column("pet_race", sa.String(length=50), nullable=True),
        sa.Column("pet_datebirth", sa.Date(), nullable=True),
        sa.Column("pet_microchip", sa.String(length=50), nullable=True),
        sa.Column("pet_gender", sa.String(length=20), nullable=True),
        sa.Column("pet_color", sa.String(length=50), nullable=True),
        sa.Column("pet_reproductive_status", sa.String(length=50), nullable=True),
        sa.Column("pet_tutor_name", sa.String(length=50), nullable=True),
        sa.Column("pet_tutor_address", sa.String(length=50), nullable=True),
        sa.Column("pet_tutor_phone", sa.String(length=15), nullable=True),
        sa.ForeignKeyConstraint(
            ["pet_user_id"], ["vetki.user_data.user_id"],
            name="fk_pet_user", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("pet_id"),
        schema="vetki",
    )

    op.create_table(
        "appointments",
        sa.Column("appointment_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("appointment_google_event_id", sa.String(length=255), nullable=True),
        sa.Column("pet_id", sa.Integer(), nullable=True),
        sa.Column("appointment_date", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"), nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["pet_id"], ["vetki.pet_data.pet_id"],
            name="appointments_pet_id_fkey", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("appointment_id"),
        schema="vetki",
    )

    op.create_table(
        "medical_records",
        sa.Column("medical_record_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("medical_record_reason", sa.String(length=20), nullable=False),
        sa.Column("medical_record_weight", sa.Float(precision=53), nullable=True),
        sa.Column("medical_record_temperature", sa.Float(precision=53), nullable=True),
        sa.Column("medical_record_heart", sa.Float(precision=53), nullable=True),
        sa.Column("medical_record_respiratory", sa.Float(precision=53), nullable=True),
        sa.Column("medical_record_water", sa.Float(precision=53), nullable=True),
        sa.Column("medical_record_capillary", sa.Float(precision=53), nullable=True),
        sa.Column("medical_record_arterial", sa.Float(precision=53), nullable=True),
        sa.Column("medical_record_date", sa.Date(), nullable=False),
        sa.Column("medical_record_medical_history", sa.Text(), nullable=True),
        sa.Column("medical_record_signals", sa.Text(), nullable=True),
        sa.Column("medical_record_diagnosis", sa.Text(), nullable=True),
        sa.Column("medical_record_treatment", sa.Text(), nullable=True),
        sa.Column("medical_record_pet_id", sa.Integer(), nullable=True),
        sa.Column("medical_record_user_id", sa.Integer(), nullable=True),
        sa.Column("medical_record_appointment_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=False),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["medical_record_pet_id"], ["vetki.pet_data.pet_id"],
            name="medical_records_medical_record_pet_id_fkey", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["medical_record_user_id"], ["vetki.user_data.user_id"],
            name="medical_records_medical_record_user_id_fkey", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["medical_record_appointment_id"], ["vetki.appointments.appointment_id"],
            name="medical_records_medical_record_appointment_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("medical_record_id"),
        schema="vetki",
    )

    op.create_table(
        "vaccinations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pet_id", sa.Integer(), nullable=False),
        sa.Column("vaccine_name", sa.String(length=120), nullable=False),
        sa.Column("application_date", sa.Date(), nullable=False),
        sa.Column("lot_number", sa.String(length=80), nullable=True),
        sa.Column("veterinarian_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"), nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["pet_id"], ["vetki.pet_data.pet_id"],
            name="vaccinations_pet_id_fkey", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="vetki",
    )

    op.execute(
        """CREATE OR REPLACE VIEW vetki.vw_medical_history AS
        SELECT r.medical_record_id, r.medical_record_reason,
               r.medical_record_weight, r.medical_record_temperature,
               r.medical_record_heart, r.medical_record_respiratory,
               r.medical_record_water, r.medical_record_capillary,
               r.medical_record_arterial, r.medical_record_date,
               r.medical_record_medical_history, r.medical_record_diagnosis,
               r.medical_record_treatment, r.medical_record_pet_id,
               r.medical_record_user_id, r.medical_record_appointment_id,
               p.pet_names, p.pet_species_name
        FROM vetki.medical_records r
        JOIN vetki.pet_data p ON r.medical_record_pet_id = p.pet_id"""
    )
    op.execute(
        """CREATE OR REPLACE VIEW vetki.vw_pet_tutor AS
        SELECT p.pet_id, p.pet_user_id, p.pet_names, p.pet_species_name,
               p.pet_race, p.pet_datebirth, p.pet_microchip, p.pet_gender,
               p.pet_color, p.pet_reproductive_status, p.pet_tutor_name,
               p.pet_tutor_address, p.pet_tutor_phone
        FROM vetki.pet_data p
        JOIN vetki.user_data u ON p.pet_user_id = u.user_id"""
    )


def downgrade():
    op.execute("DROP VIEW IF EXISTS vetki.vw_medical_history")
    op.execute("DROP VIEW IF EXISTS vetki.vw_pet_tutor")
    op.drop_table("vaccinations", schema="vetki")
    op.drop_table("medical_records", schema="vetki")
    op.drop_table("appointments", schema="vetki")
    op.drop_table("pet_data", schema="vetki")
    op.drop_table("user_data", schema="vetki")
    op.execute("DROP SCHEMA vetki")
