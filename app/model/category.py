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
        self._parent_category_uuid = parent_category_uuid
        self._name_en = name_en
        self._name_it = name_it
        self._name_es = name_es
        self._name_fr = name_fr
        self._name_ja = name_ja
        self._name_de = name_de

    @property
    def parent_category_uuid(self):
        return self._parent_category_uuid

    @parent_category_uuid.setter
    def parent_category_uuid(self, value):
        self._parent_category_uuid = value

    @property
    def name_en(self):
        return self._name_en

    @name_en.setter
    def name_en(self, value):
        self._name_en = value

    @property
    def name_it(self):
        return self._name_it

    @name_it.setter
    def name_it(self, value):
        self._name_it = value    

    @property
    def name_es(self):
        return self._name_es

    @name_es.setter
    def name_es(self, value):
        self._name_es = value        

    @property
    def name_fr(self):
        return self._name_fr

    @name_fr.setter
    def name_fr(self, value):
        self._name_fr = value    

    @property
    def name_ja(self):
        return self._name_ja

    @name_ja.setter
    def name_ja(self, value):
        self._name_ja = value

    @property
    def name_de(self):
        return self._name_de

    @name_de.setter
    def name_de(self, value):
        self._name_de = value    

    @classmethod
    def find_by_foursquare_id(cls, foursquare_id):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()).where('foursquare_id').equals(foursquare_id)
        print(statement.query)
        cur.execute(statement.query)

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

        statement = cls.select().from_table(cls.table_name()).where('yelp_alias').equals(yelp_alias)
        print(statement.query)
        cur.execute(statement.query)

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

        statement = cls.select().from_table(cls.table_name()).where('name_de').equals(name_de)
        print(statement.query)
        cur.execute(statement.query)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance