from db.model import Model
from psycopg2.extensions import AsIs
import db.connection as db_con


class Location(Model):
    def __init__(self,
                 name=None,
                 description=None,
                 street=None,
                 zip=None,
                 city=None,
                 country=None,
                 phone=None,
                 email=None,
                 website=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.phone = phone
        self.city = city
        self.street = street
        self.description = description
        self.name = name
        self.zip = zip
        self.country = country
        self.website = website

    def insert(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('INSERT INTO %s '
                    '(uuid, name, description, email, phone, city, street, zip, country, website) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (AsIs(self.table_name()), self.uuid, self.name, self.description, self.email,
                     self.phone, self.city, self.street, self.zip, self.country, self.website))
        con.commit()
        cur.close()
        con.close()
