"""Pricebenefit

Revision ID: 9e7224de733c
Revises: 46bdd472b6d5
Create Date: 2024-11-26 22:29:28.716574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e7224de733c'
down_revision: Union[str, None] = '46bdd472b6d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('benefits', sa.Column('price', sa.Integer(), server_default='0', nullable=False))
    op.add_column('stat_history_user_benefits', sa.Column('price', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stat_history_user_benefits', 'price')
    op.drop_column('benefits', 'price')
    # ### end Alembic commands ###
