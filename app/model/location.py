import app.db.connection as db_con

from app.db.model import Model
from app.db.statements import Select


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

    @classmethod
    def find_by_foursquare_id(cls, foursquare_id:str):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()).where('foursquare_id').equals(foursquare_id)
        cur.execute(statement.query)

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

        statement = cls.select().from_table(cls.table_name()).where('gelbeseiten_id').equals(gelbeseiten_id)
        cur.execute(statement.query)

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

        statement = cls.select().from_table(cls.table_name()).where('yelp_id').equals(yelp_id)
        cur.execute(statement.query)

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

        statement = cls.select().from_table(cls.table_name()).where('street').equals(street).and_column('city_uuid').equals(city_uuid).and_column('name').equals(name)
        cur.execute(statement.query)

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

        statement = 'SELECT location.*, c.* FROM location ' \
                    '   JOIN location_category ON location.uuid = location_category.location_uuid ' \
                    '   JOIN category c on location_category.category_uuid = c.uuid ' \
                    'WHERE location.gelbeseiten_id = \'%s\'' % gelbeseiten_id
        cur.execute(statement)

        # For each entry create a new instance
        entry = cur.fetchall()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance    