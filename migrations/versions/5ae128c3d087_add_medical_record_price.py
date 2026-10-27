"""Add total price to medical records.

Revision ID: 5ae128c3d087
Revises: 9c17a4e2b603
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa


revision = "5ae128c3d087"
down_revision = "9c17a4e2b603"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "medical_records",
        sa.Column(
            "medical_record_price",
            sa.Numeric(14, 2),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
        schema="vetki",
    )


def downgrade():
    op.drop_column("medical_records", "medical_record_price", schema="vetki")
