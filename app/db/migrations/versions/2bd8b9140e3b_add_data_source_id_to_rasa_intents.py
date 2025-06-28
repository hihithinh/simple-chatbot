"""add data_source_id to rasa_intents

Revision ID: 2bd8b9140e3b
Revises: f813693e1955
Create Date: 2025-06-28 16:54:21.648142

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '2bd8b9140e3b'
down_revision = 'f813693e1955'
branch_labels = None
depends_on = None


def upgrade():
    # Thêm cột data_source_id vào bảng rasa_intents
    op.add_column('rasa_intents', sa.Column('data_source_id', sa.Integer(), nullable=True))
    
    # Tạo foreign key từ rasa_intents.data_source_id đến data_sources.id
    op.create_foreign_key(
        'fk_rasa_intents_data_source_id_data_sources',
        'rasa_intents', 'data_sources',
        ['data_source_id'], ['id']
    )


def downgrade():
    # Xóa foreign key
    op.drop_constraint('fk_rasa_intents_data_source_id_data_sources', 'rasa_intents', type_='foreignkey')
    
    # Xóa cột data_source_id
    op.drop_column('rasa_intents', 'data_source_id')
