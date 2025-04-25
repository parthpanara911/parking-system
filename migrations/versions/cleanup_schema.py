"""Clean up database schema

Revision ID: cleanup_schema
Revises: 3f379d39b4c1
Create Date: 2024-05-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision = 'cleanup_schema'
down_revision = '3f379d39b4c1'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database."""
    conn = op.get_bind()
    inspector = inspect(conn)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    if not table_exists(table_name):
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def execute_with_safety(sql):
    """Execute a SQL statement with error handling."""
    conn = op.get_bind()
    try:
        conn.execute(text(sql))
        return True
    except Exception as e:
        print(f"Warning: Error executing SQL: {e}")
        return False


def upgrade():
    conn = op.get_bind()
    
    # First disable foreign key checks - this is crucial to break dependency cycles
    execute_with_safety("SET FOREIGN_KEY_CHECKS=0")
    
    try:
        # Remove payment_id column from bookings table if it exists
        if table_exists('bookings') and column_exists('bookings', 'payment_id'):
            try:
                # Directly using raw SQL to avoid constraint errors
                execute_with_safety("ALTER TABLE bookings DROP FOREIGN KEY IF EXISTS bookings_ibfk_3")
                execute_with_safety("ALTER TABLE bookings DROP COLUMN payment_id")
            except Exception as e:
                print(f"Warning: Error removing payment_id column: {e}")
        
        # Drop tables only if they exist
        tables_to_drop = ['sensor_data', 'wallet_transactions', 'wallets', 'reviews', 'payments']
        for table in tables_to_drop:
            if table_exists(table):
                try:
                    # Using direct SQL instead of op.drop_table to work around constraint issues
                    execute_with_safety(f"DROP TABLE IF EXISTS {table}")
                except Exception as e:
                    print(f"Warning: Could not drop table {table}: {e}")
        
        # Remove columns from parking_locations table if they exist
        if table_exists('parking_locations'):
            cols_to_drop = ['has_covered_parking', 'has_ev_charging', 'has_disabled_access', 
                           'has_cctv', 'has_security', 'rating']
            for col in cols_to_drop:
                if column_exists('parking_locations', col):
                    try:
                        execute_with_safety(f"ALTER TABLE parking_locations DROP COLUMN {col}")
                    except Exception as e:
                        print(f"Warning: Could not drop column {col} from parking_locations: {e}")
        
        # Remove columns from parking_slots table if they exist
        if table_exists('parking_slots'):
            cols_to_drop = ['level', 'slot_type', 'slot_size', 'sensor_id']
            for col in cols_to_drop:
                if column_exists('parking_slots', col):
                    try:
                        execute_with_safety(f"ALTER TABLE parking_slots DROP COLUMN {col}")
                    except Exception as e:
                        print(f"Warning: Could not drop column {col} from parking_slots: {e}")
        
        # Remove columns from vehicles table if they exist
        if table_exists('vehicles'):
            cols_to_drop = ['make', 'model']
            for col in cols_to_drop:
                if column_exists('vehicles', col):
                    try:
                        execute_with_safety(f"ALTER TABLE vehicles DROP COLUMN {col}")
                    except Exception as e:
                        print(f"Warning: Could not drop column {col} from vehicles: {e}")
    
    finally:
        # Re-enable foreign key checks
        execute_with_safety("SET FOREIGN_KEY_CHECKS=1")


def downgrade():
    # Add payment_id column to bookings table
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('bookings_ibfk_3', 'payments', ['payment_id'], ['id'], ondelete='SET NULL')
    
    # Add columns to vehicles table
    with op.batch_alter_table('vehicles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('make', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('model', sa.String(length=50), nullable=True))
    
    # Add columns to parking_slots table
    with op.batch_alter_table('parking_slots', schema=None) as batch_op:
        batch_op.add_column(sa.Column('level', sa.Integer(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('slot_type', sa.String(length=50), nullable=True, server_default='standard'))
        batch_op.add_column(sa.Column('slot_size', sa.String(length=20), nullable=True, server_default='standard'))
        batch_op.add_column(sa.Column('sensor_id', sa.String(length=50), nullable=True))
    
    # Add columns to parking_locations table
    with op.batch_alter_table('parking_locations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('has_covered_parking', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('has_ev_charging', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('has_disabled_access', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('has_cctv', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('has_security', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('rating', sa.Float(), nullable=True, server_default='0.0'))
    
    # Create tables (simplified schema recreation)
    # payments table
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('payment_reference', sa.String(length=50), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_reference')
    )
    
    # reviews table
    op.create_table('reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # wallets table
    op.create_table('wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('balance', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # wallet_transactions table
    op.create_table('wallet_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('transaction_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # sensor_data table
    op.create_table('sensor_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parking_slot_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('is_occupied', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['parking_slot_id'], ['parking_slots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensor_data_timestamp'), 'sensor_data', ['timestamp'], unique=False) 