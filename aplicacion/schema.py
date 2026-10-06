"""Metadatos SQLAlchemy del esquema que controla Flask-Migrate."""

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)


metadata = MetaData(schema="vetki")


user_data=Table(
    "user_data",
    metadata,
    Column("user_id", Integer, primary_key=True, autoincrement=True),
    Column("user_google_id", String(255)),
    Column("user_names", String(40), nullable=False),
    Column("user_email", String(100)),
    Column("user_rut", String(20)),
    Column("user_password", String(255)),
    Column("user_role", String(20), server_default=text("'veterinario'")),
    UniqueConstraint("user_google_id", name="user_data_user_google_id_key"),
)

pet_data=Table(
    "pet_data",
    metadata,
    Column("pet_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "pet_user_id",
        Integer,
        ForeignKey("vetki.user_data.user_id", name="fk_pet_user", ondelete="CASCADE"),
    ),
    Column("pet_species_name", String(50)),
    Column("pet_names", String(100), nullable=False),
    Column("pet_race", String(50)),
    Column("pet_datebirth", Date),
    Column("pet_microchip", String(50)),
    Column("pet_gender", String(20)),
    Column("pet_color", String(50)),
    Column("pet_reproductive_status", String(50)),
    Column("pet_tutor_name", String(50)),
    Column("pet_tutor_address", String(50)),
    Column("pet_tutor_phone", String(15)),
)

appointments=Table(
    "appointments",
    metadata,
    Column("appointment_id", Integer, primary_key=True, autoincrement=True),
    
    # 1. Agregamos el motivo/título de la cita (ej. "Control", "Vacunación")
    Column("appointment_reason", String(255), nullable=True),
    
    Column(
        "pet_id",
        Integer,
        ForeignKey(
            "vetki.pet_data.pet_id",
            name="appointments_pet_id_fkey",
            ondelete="CASCADE",
        ),
    ),
    # 2. Fecha y hora de inicio de la cita
    Column("appointment_date", DateTime(timezone=False), nullable=False),
    
    # 3. Fecha y hora de fin (súper útil para el bloque de tiempo en el calendario visual)
    Column("appointment_end_date", DateTime(timezone=False), nullable=True),
    
    Column("created_at", DateTime(timezone=True), server_default=text("NOW()")),
)

medical_records=Table(
    "medical_records",
    metadata,
    Column("medical_record_id", Integer, primary_key=True, autoincrement=True),
    Column("medical_record_reason", String(20), nullable=False),
    Column("medical_record_weight", Float(precision=53)),
    Column("medical_record_temperature", Float(precision=53)),
    Column("medical_record_heart", Float(precision=53)),
    Column("medical_record_respiratory", Float(precision=53)),
    Column("medical_record_water", Float(precision=53)),
    Column("medical_record_capillary", Float(precision=53)),
    Column("medical_record_arterial", Float(precision=53)),
    Column("medical_record_date", Date, nullable=False),
    Column("medical_record_medical_history", Text),
    Column("medical_record_signals", Text),
    Column("medical_record_diagnosis", Text),
    Column("medical_record_treatment", Text),
    Column(
        "medical_record_pet_id",
        Integer,
        ForeignKey(
            "vetki.pet_data.pet_id",
            name="medical_records_medical_record_pet_id_fkey",
            ondelete="CASCADE",
        ),
    ),
    Column(
        "medical_record_user_id",
        Integer,
        ForeignKey(
            "vetki.user_data.user_id",
            name="medical_records_medical_record_user_id_fkey",
            ondelete="CASCADE",
        ),
    ),
    Column(
        "medical_record_appointment_id",
        Integer,
        ForeignKey(
            "vetki.appointments.appointment_id",
            name="medical_records_medical_record_appointment_id_fkey",
            ondelete="CASCADE",
        ),
    ),
    Column("created_at", DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP")),
)

vaccinations=Table(
    "vaccinations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "pet_id",
        Integer,
        ForeignKey(
            "vetki.pet_data.pet_id",
            name="vaccinations_pet_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    ),
    Column("vaccine_name", String(120), nullable=False),
    Column("application_date", Date, nullable=False),
    Column("lot_number", String(80)),
    Column("veterinarian_notes", Text),
    Column("created_at", DateTime(timezone=True), server_default=text("NOW()")),
    Column("migration_test", String(20)),
)
