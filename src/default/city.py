import db.connection as db_con

from db.model import Model
from psycopg2.extensions import AsIs
from db.statements import Select

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

    @classmethod
    def delete_all_for_country_code(cls, country_code):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('DELETE FROM %s WHERE alpha_2_code = %s', (AsIs(cls.table_name()), country_code,))

        con.commit()
        cur.close()
        con.close()

    @classmethod
    def find_by_zip_and_cc(cls, zip, cc):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = Select.select().from_table(cls.table_name()).where('zip').posix('.*%s.*' % zip).and_column('alpha_2_code').equals(cc)
        print(statement.query)
        cur.execute(statement.query)

        entry = cur.fetchone()
        city_entry = None
        if entry:
            city_entry = cls(**entry)

        cur.close()
        con.close()

        return city_entry

