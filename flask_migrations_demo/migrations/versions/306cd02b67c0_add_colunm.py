"""add colunm

Revision ID: 306cd02b67c0
Revises: 56026c6a3234
Create Date: 2023-02-27 15:13:16.492068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '306cd02b67c0'
down_revision = '56026c6a3234'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('author', sa.String(), nullable=False))
    op.add_column('books', sa.Column('title', sa.String(), nullable=False))
    op.add_column('books', sa.Column('description', sa.String(), nullable=True))
    op.drop_column('books', 'Author')
    op.drop_column('books', 'Title')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('Title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('books', sa.Column('Author', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('books', 'description')
    op.drop_column('books', 'title')
    op.drop_column('books', 'author')
    # ### end Alembic commands ###
