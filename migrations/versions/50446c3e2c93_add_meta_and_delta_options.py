"""Add META and DELTA options

Revision ID: 50446c3e2c93
Revises: a090dd5c7f79
Create Date: 2019-06-07 14:38:05.538902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "50446c3e2c93"
down_revision = "a090dd5c7f79"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("application", sa.Column("delta", sa.Boolean(), nullable=True))
    op.add_column("application", sa.Column("meta", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("application", "meta")
    op.drop_column("application", "delta")
    # ### end Alembic commands ###
