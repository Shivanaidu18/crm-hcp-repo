"""Initial tables: hcps and interactions

Revision ID: 0001_initial
Revises: 
Create Date: 2025-04-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'hcps',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('specialty', sa.String(255)),
        sa.Column('hospital', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'interactions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('hcp_name', sa.String(255)),
        sa.Column('hcp_id', sa.Integer(), nullable=True),
        sa.Column('interaction_type', sa.String(100), server_default='Meeting'),
        sa.Column('date', sa.String(20)),
        sa.Column('time', sa.String(10)),
        sa.Column('attendees', sa.Text()),
        sa.Column('topics_discussed', sa.Text()),
        sa.Column('materials_shared', sa.Text()),
        sa.Column('samples_distributed', sa.Text()),
        sa.Column('sentiment', sa.String(20), server_default='Neutral'),
        sa.Column('outcomes', sa.Text()),
        sa.Column('follow_up_actions', sa.Text()),
        sa.Column('ai_suggested_followups', JSON),
        sa.Column('raw_chat_log', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Seed some HCP data
    op.execute("""
        INSERT INTO hcps (name, specialty, hospital, email) VALUES
        ('Dr. Arjun Sharma', 'Oncology', 'Apollo Hospitals', 'arjun.sharma@apollo.com'),
        ('Dr. Priya Mehta', 'Cardiology', 'AIIMS Delhi', 'priya.mehta@aiims.edu'),
        ('Dr. Rajesh Kumar', 'Neurology', 'Fortis Healthcare', 'r.kumar@fortis.in'),
        ('Dr. Anita Desai', 'Endocrinology', 'Narayana Health', 'a.desai@narayana.com'),
        ('Dr. Smith', 'General Medicine', 'City Medical Center', 'smith@citymed.com')
    """)


def downgrade() -> None:
    op.drop_table('interactions')
    op.drop_table('hcps')
