"""Update table Venue

Revision ID: f39b953b6e82
Revises: 181235923669
Create Date: 2024-04-13 22:41:04.526751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f39b953b6e82'
down_revision = '181235923669'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('website_link', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('is_talent', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.drop_column('is_talent')
        batch_op.drop_column('seeking_description')
        batch_op.drop_column('website_link')
        batch_op.drop_column('genres')

    # ### end Alembic commands ###