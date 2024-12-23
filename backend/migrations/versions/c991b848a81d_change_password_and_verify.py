"""Change password and verify

Revision ID: c991b848a81d
Revises: 77b84c7e8e9b
Create Date: 2024-11-23 00:08:53.751288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c991b848a81d'
down_revision: Union[str, None] = '77b84c7e8e9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_codes', sa.Column('time_change_password', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('date_when_change_password', sa.Date(), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'date_when_change_password')
    op.drop_column('user_codes', 'time_change_password')
    # ### end Alembic commands ###
