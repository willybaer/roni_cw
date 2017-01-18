from db.model import Model
from psycopg2.extensions import AsIs
import db.connection as db_con


class City(Model):
    def __init__(self,
                 zip=None,
                 city=None,
                 state=None,
                 latitude=None,
                 longitude=None,
                 country='Deutschland',
                 **kwargs):
        super().__init__(**kwargs)
        self.longitude = longitude
        self.latitude = latitude
        self.state = state
        self.country = country
        self.city = city
        self.zip = zip

    def insert(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('INSERT INTO %s '
                    '(uuid, zip, city, country, state, latitude, longitude) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (AsIs(self.table_name()), self.uuid, self.zip, self.city, self.country,
                     self.state, self.latitude, self.longitude))
        con.commit()
        cur.close()
        con.close()
