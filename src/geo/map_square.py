from psycopg2.extensions import AsIs
from db.model import Model

import db.connection as db_con


class MapSquare(Model):
    def __init__(self, id=None, top_right=None, bottom_left=None, query_type='FOURSQUARE_VENUE', queried_at=None):
        self.id = id
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.query_type = query_type
        self.queried_at = queried_at

    def insert(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('INSERT INTO %s '
                    '(bottom_left, '
                    'top_right, '
                    'query_type)'
                    'VALUES (%s, %s, %s) RETURNING id',
                    (AsIs(self.table_name()),
                     self.bottom_left,
                     self.top_right,
                     self.query_type))

        self.id = cur.fetchone()[0]
        con.commit()
        cur.close()
        con.close()

    def update_queried_at(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('UPDATE %s '
                    'SET '
                    '  queried_at = CURRENT_TIMESTAMP '
                    'WHERE id = %s',
                    (AsIs(self.table_name()),
                     self.id))
        con.commit()
        cur.close()
        con.close()
