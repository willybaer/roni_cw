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
                 canton=None,
                 alpha_2_code='DE',
                 website=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.longitude = longitude
        self.latitude = latitude
        self.state = state
        self.country = country
        self.city = city
        self.zip = zip
        self.canton = canton
        self.alpha_2_code = alpha_2_code
        self.website = website

    def insert(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('INSERT INTO %s '
                    '(uuid, zip, city, country, state, latitude, longitude, canton, alpha_2_code, website) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (AsIs(self.table_name()), self.uuid, self.zip, self.city, self.country,
                     self.state, self.latitude, self.longitude, self.canton, self.alpha_2_code, self.website))
        con.commit()
        cur.close()
        con.close()

    @classmethod
    def delete_all_for_country_code(cls, country_code):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('DELETE FROM %s WHERE alpha_2_code = %s', (AsIs(cls.table_name()), country_code,))

        con.commit()
        cur.close()
        con.close()

