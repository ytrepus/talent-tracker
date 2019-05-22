"""Add Gender and Sexuality tables and associate with ChangeableProtectedCharacteristics

Revision ID: 941671d6346a
Revises: fbcfff699099
Create Date: 2019-05-21 15:54:15.481172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '941671d6346a'
down_revision = 'fbcfff699099'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gender',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sexuality',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('changeable_protected_characteristics', sa.Column('sexuality_id', sa.Integer(), nullable=True))
    op.add_column('changeable_protected_characteristics', sa.Column('gender_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'changeable_protected_characteristics', 'sexuality', ['sexuality_id'], ['id'])
    op.create_foreign_key(None, 'changeable_protected_characteristics', 'gender', ['gender_id'], ['id'])
    op.drop_column('changeable_protected_characteristics', 'belief')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('changeable_protected_characteristics', sa.Column('belief', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_constraint('changeable_protected_characteristics_gender_id_fkey', 'changeable_protected_characteristics', type_='foreignkey')
    op.drop_constraint('changeable_protected_characteristics_sexuality_id_fkey', 'changeable_protected_characteristics', type_='foreignkey')
    op.drop_column('changeable_protected_characteristics', 'gender_id')
    op.drop_column('changeable_protected_characteristics', 'sexuality_id')
    op.drop_table('sexuality')
    op.drop_table('gender')
    # ### end Alembic commands ###