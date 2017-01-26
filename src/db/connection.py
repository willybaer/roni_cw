import psycopg2
import db.config as config_file
import logging
from psycopg2.extras import DictCursor

DB_CONFIG = next(iter(config_file.db_config.values()))


def connection(config=DB_CONFIG):
    logging.info(DB_CONFIG)
    return psycopg2.connect(' '.join(config))


def cursor(con):
    return con.cursor(cursor_factory=DictCursor)
