"""create users collection index

Revision ID: e4254ae01919
Revises:
Create Date: 2025-09-28 02:58:52.481696

"""
import asyncio
from typing import Sequence, Union

from pymongo import ASCENDING

from models.user import User
from services.mongodb import mongodb_service

# revision identifiers, used by Alembic.
revision: str = 'e4254ae01919'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


async def do_upgrade():
    async with mongodb_service() as mongo:
        await mongo.create_index(User, keys=[('username', ASCENDING)], unique=True, name='username_index')


async def do_downgrade():
    async with mongodb_service() as mongo:
        await mongo.drop_index(User, name='username_index')


def upgrade() -> None:
    asyncio.run(do_upgrade())


def downgrade() -> None:
    asyncio.run(do_downgrade())
