import db.connection as db_con
import uuid as UUID

from psycopg2.extensions import AsIs
from db.query.model import Model
from db.query.statements import Select

class MapSquare(Model):
    def __init__(self, uuid=None, top_right=None, bottom_left=None, query_type='FOURSQUARE_VENUE', queried_at=None, yelp_queried_at=None):
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.query_type = query_type
        self.queried_at = queried_at
        self.yelp_queried_at = yelp_queried_at
        self.uuid = uuid
        if not self.uuid:
            self.uuid = str(UUID.uuid4())

    def update_queried_at(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('UPDATE %s '
                    'SET '
                    '  queried_at = CURRENT_TIMESTAMP '
                    'WHERE uuid = %s',
                    (AsIs(self.table_name()),
                     self.uuid))
        con.commit()
        cur.close()
        con.close()

    def update_yelp_queried_at(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('UPDATE %s '
                    'SET '
                    '  yelp_queried_at = CURRENT_TIMESTAMP '
                    'WHERE uuid = %s',
                    (AsIs(self.table_name()),
                     self.uuid))
        con.commit()
        cur.close()
        con.close()

    @classmethod
    def find_all_not_queried(cls):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = Select.select().from_table(cls.table_name()).where('queried_at').is_null().limit(10000)
        print(statement.query)
        cur.execute(statement.query)

        # For each entry create a new instance
        entries = cur.fetchall()
        model_instances = []
        for entry in entries:
            m = cls(**entry)
            model_instances.append(m)

        cur.close()
        con.close()

        return model_instances

    @classmethod
    def find_all_yelp_not_queried(cls):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = Select.select().from_table(cls.table_name()).where('yelp_queried_at').is_null().limit(10000)
        print(statement.query)
        cur.execute(statement.query)

        # For each entry create a new instance
        entries = cur.fetchall()
        model_instances = []
        for entry in entries:
            m = cls(**entry)
            model_instances.append(m)

        cur.close()
        con.close()

        return model_instances

    @classmethod
    def insert_all(cls, squares):
        con = db_con.connection()
        cur = db_con.cursor(con)

        for square in squares:
            cur.execute(square.insert_statement(), square.insert_values())
            con.commit()

        cur.close()
        con.close()
