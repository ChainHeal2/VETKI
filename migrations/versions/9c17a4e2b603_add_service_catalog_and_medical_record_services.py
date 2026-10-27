"""Add service catalog and medical record service history.

Revision ID: 9c17a4e2b603
Revises: f4319b79a072
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa


revision = "9c17a4e2b603"
down_revision = "f4319b79a072"
branch_labels = None
depends_on = None


INITIAL_SERVICES = [
    ("Generales", "Microchip"),
    ("Generales", "Consulta"),
    ("Vacunas", "Vacuna séxtuple/óctuple"),
    ("Vacunas", "Vacuna antirrábica"),
    ("Vacunas", "Vacuna leucemia"),
    ("Vacunas", "Vacuna triple felina"),
    ("Vacunas", "Vacuna KC"),
    ("Desparasitación", "Desparasitación interna"),
    ("Desparasitación", "Desparasitación externa"),
    ("Cuidados", "Corte de uñas"),
    ("Cuidados", "Limpieza de oídos"),
    ("Cuidados", "Limpieza simple"),
    ("Cuidados", "Limpieza compleja"),
    ("Suplementos", "Inyectable simple"),
    ("Suplementos", "Inyectable especial"),
]


def upgrade():
    op.create_table(
        "services",
        sa.Column("service_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("service_name", sa.String(length=120), nullable=False),
        sa.Column("service_category", sa.String(length=60), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("TRUE"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("service_id", name="pk_services"),
        sa.UniqueConstraint(
            "service_category",
            "service_name",
            name="uq_services_category_name",
        ),
        schema="vetki",
    )

    op.create_table(
        "medical_record_services",
        sa.Column("medical_record_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("service_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["medical_record_id"],
            ["vetki.medical_records.medical_record_id"],
            name="fk_medical_record_services_record",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["vetki.services.service_id"],
            name="fk_medical_record_services_service",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "medical_record_id", "service_id", name="pk_medical_record_services"
        ),
        schema="vetki",
    )

    services_table = sa.table(
        "services",
        sa.column("service_name", sa.String()),
        sa.column("service_category", sa.String()),
        sa.column("is_active", sa.Boolean()),
        schema="vetki",
    )
    op.bulk_insert(
        services_table,
        [
            {
                "service_name": name,
                "service_category": category,
                "is_active": True,
            }
            for category, name in INITIAL_SERVICES
        ],
    )


def downgrade():
    op.drop_table("medical_record_services", schema="vetki")
    op.drop_table("services", schema="vetki")
