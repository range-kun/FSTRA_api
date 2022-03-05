import json
from functools import partial

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, json_serializer=partial(json.dumps, ensure_ascii=False))
metadata = sa.MetaData()

pereval_added_table: sa.Table = sa.Table(
    "pereval_added",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("date_added", sa.DateTime),
    sa.Column("raw_data", sa.JSON),
    sa.Column("images", sa.JSON),
    sa.Column("status", sa.VARCHAR(length=20))
)

pereval_images_table: sa.Table = sa.Table(
    "pereval_images",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("date_added", sa.DateTime),
    sa.Column("img", BYTEA),
    sa.Column('pereval_added_id',
              sa.Integer,
              sa.ForeignKey("pereval_added.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
              ),
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
