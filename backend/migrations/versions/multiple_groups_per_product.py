"""multiple groups per product

Revision ID: multiple_groups_per_product
Revises: cc13a695bbe8
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'multiple_groups_per_product'
down_revision = 'cc13a695bbe8'
branch_labels = None
depends_on = None


def upgrade():
    # Remove unique constraint on product_id in telegram_groups table
    with op.batch_alter_table('telegram_groups', schema=None) as batch_op:
        batch_op.drop_constraint('telegram_groups_product_id_key', type_='unique')


def downgrade():
    # Add back unique constraint on product_id in telegram_groups table
    with op.batch_alter_table('telegram_groups', schema=None) as batch_op:
        batch_op.create_unique_constraint('telegram_groups_product_id_key', ['product_id'])