"""Initial schema: customers, leads, contact_events, opportunities, idempotency_keys

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('primary_email', sa.String(), nullable=True),
        sa.Column('primary_phone', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('prospect', 'active', 'inactive', name='customerstatus'), nullable=False, server_default='prospect'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_customers_primary_email'), 'customers', ['primary_email'], unique=False)
    op.create_index(op.f('ix_customers_primary_phone'), 'customers', ['primary_phone'], unique=False)

    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source', sa.Enum('facebook', 'instagram', 'website', 'manual', 'other', name='leadsource'), nullable=False),
        sa.Column('status', sa.Enum('new', 'needs_info', 'qualified', 'disqualified', name='leadstatus'), nullable=False, server_default='new'),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('owner_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('missing_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('qualification_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    )
    op.create_index(op.f('ix_leads_customer_id'), 'leads', ['customer_id'], unique=False)
    op.create_index(op.f('ix_leads_email'), 'leads', ['email'], unique=False)
    op.create_index(op.f('ix_leads_phone'), 'leads', ['phone'], unique=False)

    # Create contact_events table
    op.create_table(
        'contact_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('channel', sa.Enum('sms', 'email', 'phone', 'note', 'system', 'automation', name='contactchannel'), nullable=False),
        sa.Column('direction', sa.Enum('inbound', 'outbound', 'internal', name='contactdirection'), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
    )
    op.create_index(op.f('ix_contact_events_customer_id'), 'contact_events', ['customer_id'], unique=False)
    op.create_index(op.f('ix_contact_events_lead_id'), 'contact_events', ['lead_id'], unique=False)
    op.create_index(op.f('ix_contact_events_created_at'), 'contact_events', ['created_at'], unique=False)

    # Create opportunities table
    op.create_table(
        'opportunities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('stage', sa.Enum('new', 'quoting', 'followup', 'won', 'lost', name='opportunitystage'), nullable=False, server_default='new'),
        sa.Column('value_estimate', sa.Numeric(10, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
    )
    op.create_index(op.f('ix_opportunities_customer_id'), 'opportunities', ['customer_id'], unique=False)

    # Create idempotency_keys table
    op.create_table(
        'idempotency_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_idempotency_keys_key'), 'idempotency_keys', ['key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_idempotency_keys_key'), table_name='idempotency_keys')
    op.drop_table('idempotency_keys')
    op.drop_index(op.f('ix_opportunities_customer_id'), table_name='opportunities')
    op.drop_table('opportunities')
    op.drop_index(op.f('ix_contact_events_created_at'), table_name='contact_events')
    op.drop_index(op.f('ix_contact_events_lead_id'), table_name='contact_events')
    op.drop_index(op.f('ix_contact_events_customer_id'), table_name='contact_events')
    op.drop_table('contact_events')
    op.drop_index(op.f('ix_leads_phone'), table_name='leads')
    op.drop_index(op.f('ix_leads_email'), table_name='leads')
    op.drop_index(op.f('ix_leads_customer_id'), table_name='leads')
    op.drop_table('leads')
    op.drop_index(op.f('ix_customers_primary_phone'), table_name='customers')
    op.drop_index(op.f('ix_customers_primary_email'), table_name='customers')
    op.drop_table('customers')
