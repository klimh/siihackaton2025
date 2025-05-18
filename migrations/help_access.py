"""Migration for adding the HelpAccess table."""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001_help_access'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add HelpAccess table."""
    op.create_table(
        'help_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_help_access_timestamp'), 'help_access', ['timestamp'], unique=False)

def downgrade():
    """Remove HelpAccess table."""
    op.drop_index(op.f('ix_help_access_timestamp'), table_name='help_access')
    op.drop_table('help_access') 