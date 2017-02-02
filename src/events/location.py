import db.connection as db_con
from db.model import Model
from db.statements import Select


class Location(Model):
    def __init__(self,
                 city_uuid=None,
                 foursquare_id=None,
                 name=None,
                 description=None,
                 street=None,
                 phone=None,
                 email=None,
                 website=None,
                 latitude=None,
                 longitude=None,
                 yelp_id=None,
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

    @classmethod
    def find_by_foursquare_id(cls, foursquare_id):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = Select.select().from_table(cls.table_name()).where('foursquare_id').equals(foursquare_id)
        cur.execute(statement.query)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance

    @classmethod
    def find_by_yelp_id(cls, yelp_id):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = Select.select().from_table(cls.table_name()).where('yelp_id').equals(yelp_id)
        cur.execute(statement.query)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance