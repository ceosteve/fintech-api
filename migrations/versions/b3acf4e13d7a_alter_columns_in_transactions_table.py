"""alter columns in transactions table

Revision ID: b3acf4e13d7a
Revises: 4b2a9cdb226e
Create Date: 2025-11-10 18:41:08.450282

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3acf4e13d7a'
down_revision: Union[str, Sequence[str], None] = '4b2a9cdb226e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Drop old foreign keys first
    op.drop_constraint('transactions_sender_wallet_account_number_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_receiver_wallet_account_number_fkey', 'transactions', type_='foreignkey')

    # Alter columns using USING clause to prevent cast errors
    op.execute("""
        ALTER TABLE transactions 
        ALTER COLUMN sender_wallet_account_number 
        TYPE BIGINT USING NULL;
    """)
    op.execute("""
        ALTER TABLE transactions 
        ALTER COLUMN receiver_wallet_account_number 
        TYPE BIGINT USING NULL;
    """)

    # Recreate foreign keys to wallets.account_number
    op.create_foreign_key(
        None, 'transactions', 'wallets',
        ['sender_wallet_account_number'], ['account_number']
    )
    op.create_foreign_key(
        None, 'transactions', 'wallets',
        ['receiver_wallet_account_number'], ['account_number']
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop new foreign keys
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_constraint(None, 'transactions', type_='foreignkey')

    # Alter columns back to UUID
    op.execute("""
        ALTER TABLE transactions 
        ALTER COLUMN sender_wallet_account_number 
        TYPE UUID USING NULL;
    """)
    op.execute("""
        ALTER TABLE transactions 
        ALTER COLUMN receiver_wallet_account_number 
        TYPE UUID USING NULL;
    """)

    # Recreate original foreign keys to wallets.id
    op.create_foreign_key(
        'transactions_sender_wallet_account_number_fkey', 'transactions', 'wallets',
        ['sender_wallet_account_number'], ['id']
    )
    op.create_foreign_key(
        'transactions_receiver_wallet_account_number_fkey', 'transactions', 'wallets',
        ['receiver_wallet_account_number'], ['id']
    )
