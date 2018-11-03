import app.db.connection as db_con

from app.db.model import Model
from app.db.statements import Select
from psycopg2.extensions import AsIs

class City(Model):
    def __init__(self,
                 postal_code=None,
                 name=None,
                 state=None,
                 latitude=None,
                 longitude=None,
                 country='Deutschland',
                 alpha_2_code='DE',
                 website=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.longitude = longitude
        self.latitude = latitude
        self.state = state
        self.country = country
        self.name = name
        self.postal_code = postal_code
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
    def find_by_postal_code_and_alpa_2_code(cls, postal_code, alpha_2_code):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()).where('postal_code').posix('.*%s.*' % postal_code).and_column('alpha_2_code').equals(alpha_2_code)
        print(statement.query)
        cur.execute(statement.query)

        entry = cur.fetchone()
        city_entry = None
        if entry:
            city_entry = cls(**entry)

        cur.close()
        con.close()

        return city_entry

