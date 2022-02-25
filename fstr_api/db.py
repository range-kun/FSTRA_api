from datetime import datetime
import json
from functools import partial

from databases import Database
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

from config import DATABASE_URL

database = Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, json_serializer=partial(json.dumps, ensure_ascii=False))
metadata = sa.MetaData()

pereval_added_table: sa.Table = sa.Table(
    "pereval_added",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("date_added", sa.DateTime, default=datetime.now()),
    sa.Column("raw_data", sa.JSON),
    sa.Column("images", sa.JSON),
    sa.Column("status", sa.VARCHAR(length=20))
)
