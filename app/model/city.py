import app.db.connection as db_con

from app.db.model import Model
from app.db.statements import Select
from app.db.helper import levenshtein_distance, levenshtein_distance_percentage
from psycopg2.extensions import AsIs

class City(Model):
    def __init__(self,
                 parent_city_uuid=None,
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
        self.parent_city_uuid = parent_city_uuid
        self.longitude = longitude
        self.latitude = latitude
        self.state = state
        self.country = country
        self.name = name
        self.alpha_2_code = alpha_2_code
        self.website = website
        self.districts = []

        value = postal_code
        if type(value) is not list:
            value = [postal_code]
        self.__postal_code = value

    @property
    def postal_code(self):
        return self.__postal_code

    @postal_code.setter
    def postal_code(self, v):
        value = v
        if type(value) is not list:
            value = [v]
        self.__postal_code = value

    def excluded_atts(self) -> list:
        atts = super().excluded_atts()
        atts.append('districts')
        return atts

    @classmethod
    def delete_all_for_country_code(cls, country_code):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('DELETE FROM %s WHERE alpha_2_code = %s', (AsIs(cls.table_name()), country_code,))
        con.commit()
        
        cur.close()
        con.close()

    @classmethod
    def find_by_postal_code_and_alpa_2_code(cls, postal_code, alpha_2_code, parent_city_uuid=None):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()) \
                .where('\'%s\'' % postal_code).equals('ANY(postal_code)', check_for_qoute=False) \
                .and_column('alpha_2_code').equals(alpha_2_code)
        if parent_city_uuid is None:
            statement = statement.and_column('parent_city_uuid').is_null().build()      
        else:
            statement = statement.and_column('parent_city_uuid').equals(parent_city_uuid).build()            

        print(statement)
        cur.execute(statement)

        entries = cur.fetchall()
        city_entries = []
        for entry in entries:
            city_entries.append(cls(**entry))

        cur.close()
        con.close()

        return city_entries

    @classmethod
    def find_matched_city_by_postal_code_and_name(cls, postal_code, alpha_2_code, city_name):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()) \
                .left_join(table=City.table_name(), columns=['postal_code', 'name', 'uuid'], table_name='p') \
                .on('city.uuid').equals('p.parent_city_uuid') \
                .where('\'%s\'' % postal_code).equals('ANY(city.postal_code)', check_for_qoute=False) \
                .and_column('city.alpha_2_code').equals(alpha_2_code) \
                .build()
            
        print(statement)
        cur.execute(statement)

        f_entries = cur.fetchall()
        city_entry = None

        entries = {}
        for entry in f_entries:
            if entry['uuid'] in entries:
                entries[entry['uuid']].append(entry)
            else:
                entries[entry['uuid']] = [entry]    
        
        final_entries = []
        for key, parent_city_entry in entries.items():
            parent_city = cls(**parent_city_entry[0])
            for district in parent_city_entry:
                if district['p_name']:
                    values = dict((k.replace('p_', ''), v) for (k, v) in district.items() if k.startswith('p_'))
                    parent_city.districts.append(City(**values))

            final_entries.append(parent_city)

        # First iterate through all parent_city entries
        city_entry = None
        for p_city in final_entries:
            lev = levenshtein_distance(source=p_city.name, target=city_name)
            percent = lev / len(city_name)
            if lev <= 2 and percent < 0.2:    
                city_entry = p_city
                break
            for district in p_city.districts:
                district_name = district.name
                if p_city.name not in district.name:
                    district_name = '%s-%s' % (p_city.name, district.name)

                lev = levenshtein_distance_percentage(source=district_name, target=city_name)
                if lev <= 0.1:    
                    city_entry = district
                    break

            if city_entry:
                break

        cur.close()
        con.close()

        if city_entry is None and len(final_entries) > 0:
            return final_entries[0]
        return city_entry    

