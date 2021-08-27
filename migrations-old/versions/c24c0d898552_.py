"""empty message

Revision ID: c24c0d898552
Revises: 31c4fa2efc77
Create Date: 2021-08-27 15:25:25.295709

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c24c0d898552'
down_revision = '31c4fa2efc77'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('exchange_rate', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transactions', 'exchange_rate')
    # ### end Alembic commands ###