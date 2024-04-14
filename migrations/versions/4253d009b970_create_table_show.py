"""Create table Show

Revision ID: 4253d009b970
Revises: 1640a9afa86f
Create Date: 2024-04-13 22:51:03.768268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4253d009b970'
down_revision = '1640a9afa86f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Show')
    # ### end Alembic commands ###