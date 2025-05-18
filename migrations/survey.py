"""Migration for adding the Survey table."""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_survey'
down_revision = '001_help_access'
branch_labels = None
depends_on = None

def upgrade():
    """Add Survey table."""
    op.create_table(
        'survey',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('activities', sa.Text(), nullable=False),
        sa.Column('custom_activities', sa.Text(), nullable=True),
        sa.Column('social_media_time', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uix_user_date')
    )
    op.create_index(op.f('ix_survey_date'), 'survey', ['date'], unique=False)
    op.create_index(op.f('ix_survey_created_at'), 'survey', ['created_at'], unique=False)

def downgrade():
    """Remove Survey table."""
    op.drop_index(op.f('ix_survey_created_at'), table_name='survey')
    op.drop_index(op.f('ix_survey_date'), table_name='survey')
    op.drop_table('survey') 