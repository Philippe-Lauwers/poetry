"""Adding table to store previous versions of a verse

Revision ID: 9e6a7152c55d
Revises: 06da260547b4
Create Date: 2025-07-13 02:52:38.182826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e6a7152c55d'
down_revision = '06da260547b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('previousVerses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('verse_id', sa.Integer(), nullable=False),
    sa.Column('action_id', sa.Integer(), nullable=False),
    sa.Column('previousVerse', sa.String(length=1000), nullable=False),
    sa.ForeignKeyConstraint(['action_id'], ['actions.id'], name='fk_previousVerses_actions_id'),
    sa.ForeignKeyConstraint(['verse_id'], ['verses.id'], name='fk_previousVerses_verses_id'),
    sa.PrimaryKeyConstraint('id', name='pk_previousVerses')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('previousVerses')
    # ### end Alembic commands ###
