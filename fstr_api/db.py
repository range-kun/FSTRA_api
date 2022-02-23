from datetime import datetime

from databases import Database
import sqlalchemy as sa

from config import DATABASE_URL

database = Database(DATABASE_URL)
engine = sa.create_engine(DATABASE_URL)
metadata = sa.MetaData()

sa.Table(
    "pereval_added",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("data_added", sa.DateTime, default=datetime.now()),
    sa.Column("raw_data", sa.JSON),
    sa.Column("images", sa.JSON)
)
