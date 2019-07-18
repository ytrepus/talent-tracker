"""Add timestamp to AuditEvent

Revision ID: bfdf3ca8520e
Revises: 33a9387b9fe3
Create Date: 2019-07-12 15:52:44.289244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfdf3ca8520e'
down_revision = '33a9387b9fe3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('audit_event', sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('audit_event', 'timestamp')
    # ### end Alembic commands ###