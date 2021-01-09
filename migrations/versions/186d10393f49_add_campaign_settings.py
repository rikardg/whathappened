"""Add campaign settings

Revision ID: 186d10393f49
Revises: 8b29c4eb9589
Create Date: 2021-01-05 21:05:19.783990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '186d10393f49'
down_revision = '8b29c4eb9589'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaign', schema=None) as batch_op:
        batch_op.add_column(sa.Column('characters_enabled', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('handouts_enabled', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('npcs_enabled', sa.Boolean(), nullable=True))

    op.execute("UPDATE campaign SET characters_enabled = true")
    op.execute("UPDATE campaign SET handouts_enabled = true")
    op.execute("UPDATE campaign SET npcs_enabled = true")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaign', schema=None) as batch_op:
        batch_op.drop_column('npcs_enabled')
        batch_op.drop_column('handouts_enabled')
        batch_op.drop_column('characters_enabled')

    # ### end Alembic commands ###