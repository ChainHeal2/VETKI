"""Add patient photo bytes.

Revision ID: da821f5c17a4
Revises: c8726d4105af
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa


revision = "da821f5c17a4"
down_revision = "c8726d4105af"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "pet_data",
        sa.Column("pet_photo", sa.LargeBinary(), nullable=True),
        schema="vetki",
    )


def downgrade():
    op.drop_column("pet_data", "pet_photo", schema="vetki")
