from os import getenv

FSTR_DB_HOST = getenv("FSTR_DB_HOST", "localhost")
FSTR_DB_PORT = getenv("FSTR_DB_PORT", 5432)
FSTR_DB_LOGIN = getenv("FSTR_DB_LOGIN", "range")
FSTR_DB_PASS = getenv("FSTR_DB_PASS", "1")
DB_NAME = "postgres"
DATABASE_URL = f'postgresql+asyncpg://{FSTR_DB_LOGIN}:{FSTR_DB_PASS}@{FSTR_DB_HOST}:{FSTR_DB_PORT}/{DB_NAME}'
