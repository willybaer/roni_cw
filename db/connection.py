import psycopg2
from psycopg2.extras import DictCursor
import config as config_file


def connection(config):
    db_conf = config
    if not db_conf:
        db_conf = next(iter(config_file.db_config.values()))

    return psycopg2.connect(' '.join(db_conf))


def cursor(con):
    return con.cursor(cursor_factory=DictCursor)

