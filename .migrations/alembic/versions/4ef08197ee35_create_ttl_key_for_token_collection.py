"""create ttl key for token collection

Revision ID: 4ef08197ee35
Revises: e4254ae01919
Create Date: 2025-10-06 11:53:35.118438

"""
import asyncio
from typing import Sequence, Union

from pymongo import ASCENDING

from schemas.token import WhiteListToken
from services.mongodb import mongodb_service

# revision identifiers, used by Alembic.
revision: str = '4ef08197ee35'
down_revision: Union[str, Sequence[str], None] = 'e4254ae01919'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


async def do_upgrade():
    async with mongodb_service() as mongo:
        await mongo.create_index(WhiteListToken, keys=[('jti', ASCENDING)], name='jti_index', unique=True)
        await mongo.create_index(WhiteListToken, keys=[('_user_id', ASCENDING)], name='user_id_index')
        await mongo.create_index(WhiteListToken, keys=[('expired', ASCENDING)],
                                 expireAfterSeconds=0, name='expired_ttl')


async def do_downgrade():
    async with mongodb_service() as mongo:
        await mongo.drop_index(WhiteListToken, name='jti_index')
        await mongo.drop_index(WhiteListToken, name='user_id_index')
        await mongo.drop_index(WhiteListToken, name='expired_ttl')


def upgrade() -> None:
    asyncio.run(do_upgrade())


def downgrade() -> None:
    asyncio.run(do_downgrade())
