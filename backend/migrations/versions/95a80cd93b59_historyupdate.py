"""HistoryUpdate

Revision ID: 95a80cd93b59
Revises: 9e7224de733c
Create Date: 2024-11-30 21:28:25.565103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95a80cd93b59'
down_revision: Union[str, None] = '9e7224de733c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stat_history_user_benefits', sa.Column('user_legal_entity', sa.String(), nullable=True))
    op.add_column('stat_history_user_benefits', sa.Column('user_job_title', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stat_history_user_benefits', 'user_job_title')
    op.drop_column('stat_history_user_benefits', 'user_legal_entity')
    # ### end Alembic commands ###
