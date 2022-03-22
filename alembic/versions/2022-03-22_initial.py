"""Initial

Revision ID: b85052ccdd04
Revises: 
Create Date: 2022-03-22 21:29:40.701264

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'b85052ccdd04'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('login', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('first_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('last_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hash_pass', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('privileges', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('updated_at', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('login')
    )
    op.create_table('media_user',
    sa.Column('media_path', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('is_main', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('media_user')
    op.drop_table('user')
    # ### end Alembic commands ###