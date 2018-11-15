import app.db.connection as db_con

from app.db.model import Model
from app.db.statements import Select
from app.model.location_category import LocationCategory
from app.model.category import Category

class Location(Model):
    def __init__(self,
                 city_uuid:str=None,
                 foursquare_id:str=None,
                 name:str=None,
                 description:str=None,
                 street:str=None,
                 phone:str=None,
                 email:str=None,
                 website:str=None,
                 latitude:float=None,
                 longitude:float=None,
                 yelp_id:str=None,
                 gelbeseiten_id:str=None,
                 twitter:str=None,
                 facebook:str=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.city_uuid = city_uuid
        self.foursquare_id = foursquare_id
        self.email = email
        self.phone = phone
        self.street = street
        self.description = description
        self.name = name
        self.website = website
        self.latitude = latitude
        self.longitude = longitude
        self.yelp_id = yelp_id
        self.gelbeseiten_id = gelbeseiten_id
        self.twitter = twitter
        self.facebook = facebook
        self.categories = None

    def excluded_atts(self) -> list:
        atts = super().excluded_atts()
        atts.append('categories')
        return atts

    @classmethod
    def find_by_foursquare_id(cls, foursquare_id:str):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select() \
            .from_table(cls.table_name()) \
            .where('foursquare_id').equals(foursquare_id) \
            .build()

        cur.execute(statement)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance

    @classmethod
    def find_by_gelebeseiten_id(cls, gelbeseiten_id:str):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select() \
            .from_table(cls.table_name()) \
            .where('gelbeseiten_id').equals(gelbeseiten_id) \
            .build()

        cur.execute(statement)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance

    @classmethod
    def find_by_yelp_id(cls, yelp_id:str):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select() \
            .from_table(cls.table_name()) \
            .where('yelp_id').equals(yelp_id) \
            .build()

        cur.execute(statement)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance

    @classmethod
    def find_by_street_and_city_and_name(cls, street:str, city_uuid:str, name:str):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select() \
            .from_table(cls.table_name()) \
            .where('street').equals(street) \
            .and_column('city_uuid').equals(city_uuid) \
            .and_column('name').equals(name) \
            .build()

        cur.execute(statement)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance        

    @classmethod
    def find_by_phone_and_city_and_name(cls, phone:str, city_uuid:str, name:str):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select() \
            .from_table(cls.table_name()) \
            .where('phone').equals(phone) \
            .and_column('city_uuid').equals(city_uuid) \
            .and_column('name').equals(name) \
            .build()

        cur.execute(statement)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance        

    @classmethod
    def find_with_categories(cls, gelbeseiten_id):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select() \
            .from_table(cls.table_name()) \
            .join(table=LocationCategory.table_name()) \
                .on('%s.uuid' % Location.table_name()) \
                .equals('%s.location_uuid' % LocationCategory.table_name()) \
            .join(table=Category.table_name(), columns=['uuid', 'name_de', 'name_en', 'parent_category_uuid']) \
                .on('%s.category_uuid' % LocationCategory.table_name()) \
                .equals('%s.uuid' % Category.table_name()) \
            .where('gelbeseiten_id') \
            .equals(gelbeseiten_id) \
            .build()
        
        cur.execute(statement)

        # For each entry create a new instance
        entries = cur.fetchall()
        if len(entries) == 0:
            return None

        sub_instances = []
        for entry in entries:
            category_values = dict((k.replace('category_', ''), v) for (k, v) in entry.items() if k.startswith('category_'))
            sub_instances.append(Category(**category_values))
        
        model_instance = cls(**entries[0])
        model_instance.categories = sub_instances

        cur.close()
        con.close()

        return model_instance    