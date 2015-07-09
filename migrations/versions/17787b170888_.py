"""empty message

Revision ID: 17787b170888
Revises: 2673ce30fb12
Create Date: 2015-07-09 17:57:24.001134

"""

# revision identifiers, used by Alembic.
revision = '17787b170888'
down_revision = '2673ce30fb12'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inventory_transaction_line',
                  sa.Column('in_transit_quantity', sa.Numeric(precision=8, scale=2, decimal_return_scale=2),
                            nullable=True))
    op.alter_column('inventory_transaction_line', 'quantity',
                    existing_type=sa.NUMERIC(precision=8, scale=2), nullable=True)
    op.alter_column('receiving', 'purchase_order_id',
                    existing_type=sa.INTEGER(), nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('receiving', 'purchase_order_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('inventory_transaction_line', 'quantity', existing_type=sa.NUMERIC(precision=8, scale=2),
                    nullable=False)
    op.drop_column('inventory_transaction_line', 'in_transit_quantity')
    ### end Alembic commands ###
