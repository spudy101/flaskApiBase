"""create initial tables

Revision ID: 02a2347d330f
Revises: 
Create Date: 2025-12-20 18:30:25.469693

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '02a2347d330f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear tabla users (el ENUM se crea automáticamente)
    op.create_table('users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('user', 'admin', name='user_roles', schema='flask_schema'), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='flask_schema'
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True, schema='flask_schema')
    
    # Crear tabla login_attempts
    op.create_table('login_attempts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('blocked_until', sa.DateTime(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='flask_schema'
    )
    op.create_index(op.f('ix_login_attempts_email'), 'login_attempts', ['email'], unique=False, schema='flask_schema')
    
    # Crear tabla products (DESPUÉS de users por la FK)
    op.create_table('products',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['flask_schema.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='flask_schema'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar tablas en orden inverso
    op.drop_table('products', schema='flask_schema')
    op.drop_index(op.f('ix_login_attempts_email'), table_name='login_attempts', schema='flask_schema')
    op.drop_table('login_attempts', schema='flask_schema')
    op.drop_index(op.f('ix_users_email'), table_name='users', schema='flask_schema')
    op.drop_table('users', schema='flask_schema')
    
    # Eliminar ENUM
    op.execute('DROP TYPE IF EXISTS flask_schema.user_roles CASCADE')