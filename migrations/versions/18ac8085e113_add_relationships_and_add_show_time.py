"""add relationships and add show time

Revision ID: 18ac8085e113
Revises: f6266ff415f9
Create Date: 2020-12-21 18:37:26.550378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18ac8085e113'
down_revision = 'f6266ff415f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'created_at')
    # ### end Alembic commands ###