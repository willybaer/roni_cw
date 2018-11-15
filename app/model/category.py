import app.db.connection as db_con

from app.db.model import Model
from psycopg2.extensions import AsIs


class Category(Model):
    def __init__(self,
                 parent_category_uuid=None,
                 name_de=None,
                 name_en=None,
                 name_it=None,
                 name_es=None,
                 name_fr=None,
                 name_ja=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.parent_category_uuid = parent_category_uuid
        self.name_en = name_en
        self.name_it = name_it
        self.name_es = name_es
        self.name_fr = name_fr
        self.name_ja = name_ja
        self.name_de = name_de

    @classmethod
    def find_by_foursquare_id(cls, foursquare_id):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()).where('foursquare_id').equals(foursquare_id).build()
        print(statement)
        cur.execute(statement)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance

    @classmethod
    def find_by_yelp_alias(cls, yelp_alias):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()).where('yelp_alias').equals(yelp_alias).build()
        print(statement)
        cur.execute(statement)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance

    @classmethod
    def find_by_name_de(cls, name_de):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()).where('name_de').equals(name_de).build()
        print(statement)
        cur.execute(statement)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance