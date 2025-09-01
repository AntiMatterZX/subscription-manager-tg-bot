"""Merge migrations

Revision ID: merge_heads
Revises: change_product_id_to_string, multiple_groups_per_product
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('change_product_id_to_string', 'multiple_groups_per_product')
branch_labels = None
depends_on = None


def upgrade():
    # No changes needed, just merging heads
    pass


def downgrade():
    # No changes needed, just merging heads
    pass