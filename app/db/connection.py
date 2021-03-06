import psycopg2

from app.db.config import db_config
from psycopg2.extras import DictCursor

DB_CONFIG = next(iter(db_config.values()))

def connection():
    return psycopg2.connect(' '.join(DB_CONFIG))

def cursor(con):
    return con.cursor(cursor_factory=DictCursor)

def set_db_config(config):
    global DB_CONFIG
    DB_CONFIG = config
