"""create users collection index

Revision ID: e4254ae01919
Revises:
Create Date: 2025-09-28 02:58:52.481696

"""
import asyncio
from typing import Sequence, Union

from pymongo import ASCENDING

from schemas.user import User
from services.mongodb import MongoDBService

# revision identifiers, used by Alembic.
revision: str = 'e4254ae01919'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

mongodb_service = MongoDBService()


async def do_upgrade():
    await mongodb_service.create_index(User, keys=[('username', ASCENDING)], unique=True, name='username_index')


async def do_downgrade():
    await mongodb_service.drop_index(User, name='username_index')


def upgrade() -> None:
    asyncio.run(do_upgrade())


def downgrade() -> None:
    asyncio.run(do_downgrade())
