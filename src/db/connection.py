import psycopg2
from psycopg2.extras import DictCursor
import config as config_file

DB_CONFIG = next(iter(config_file.db_config.values()))


def connection(config=DB_CONFIG):
    return psycopg2.connect(' '.join(config))


def cursor(con):
    return con.cursor(cursor_factory=DictCursor)
