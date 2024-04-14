"""Create relationship Artist with Show

Revision ID: 9ed87a19d54c
Revises: 96b2adc3e252
Create Date: 2024-04-14 11:38:18.349534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ed87a19d54c'
down_revision = '96b2adc3e252'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('artist_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'Artist', ['artist_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('artist_id')

    # ### end Alembic commands ###
