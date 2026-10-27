"""Store medical record prices as integer CLP pesos.

Revision ID: 3b61485db910
Revises: 5ae128c3d087
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa


revision = "3b61485db910"
down_revision = "5ae128c3d087"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "medical_records",
        "medical_record_price",
        existing_type=sa.Numeric(14, 2),
        type_=sa.BigInteger(),
        existing_nullable=False,
        existing_server_default=sa.text("0.00"),
        server_default=sa.text("0"),
        postgresql_using="ROUND(medical_record_price)::BIGINT",
        schema="vetki",
    )


def downgrade():
    op.alter_column(
        "medical_records",
        "medical_record_price",
        existing_type=sa.BigInteger(),
        type_=sa.Numeric(14, 2),
        existing_nullable=False,
        existing_server_default=sa.text("0"),
        server_default=sa.text("0.00"),
        postgresql_using="medical_record_price::NUMERIC(14, 2)",
        schema="vetki",
    )
