from db.model import Model
import db.connection as db_con
from psycopg2.extensions import AsIs


class Event(Model):
    def __init__(self, locations_uuid=None, description=None, **kwargs):
        super().__init__(**kwargs)
        self.location_uuid = locations_uuid
        self.description = description

    def insert(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('INSERT INTO %s (uuid, location_uuid, description) VALUES (%s, %s, %s)',
                    (AsIs(self.table_name()), self.uuid, self.location_uuid, self.description,))
        con.commit()
        cur.close()
        con.close()
