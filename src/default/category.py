import db.connection as db_con
from db.model import Model
from psycopg2.extensions import AsIs
from db.statements import Select


class Category(Model):
    def __init__(self,
                 foursquare_id=None,
                 foursquare_icon=None,
                 parent_category_uuid=None,
                 name_de=None,
                 name_en=None,
                 name_it=None,
                 name_es=None,
                 name_fr=None,
                 name_ja=None,
                 yelp_alias=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.parent_category_uuid = parent_category_uuid
        self.name_en = name_en
        self.name_it = name_it
        self.name_es = name_es
        self.name_fr = name_fr
        self.name_ja = name_ja
        self.name_de = name_de
        self.foursquare_icon = foursquare_icon
        self.foursquare_id = foursquare_id
        self.yelp_alias = yelp_alias;

    def update(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('UPDATE %s '
                    'SET  parent_category_uuid = %s,'
                    '     foursquare_id = %s,'
                    '     foursquare_icon = %s,'
                    '     name_de = %s,'
                    '     name_en = %s,'
                    '     name_it = %s,'
                    '     name_es = %s,'
                    '     name_fr = %s,'
                    '     name_ja = %s,'
                    '     yelp_alias = %s'
                    'WHERE uuid = %s',
                    (AsIs(self.table_name()),
                     self.parent_category_uuid,
                     self.foursquare_id,
                     self.foursquare_icon,
                     self.name_de,
                     self.name_en,
                     self.name_it,
                     self.name_es,
                     self.name_fr,
                     self.name_ja,
                     self.uuid,
                     self.yelp_alias))

        con.commit()
        cur.close()
        con.close()

    @classmethod
    def find_by_foursquare_id(cls, foursquare_id):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = Select.select().from_table(cls.table_name()).where('foursquare_id').equals(foursquare_id)
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

        statement = Select.select().from_table(cls.table_name()).where('yelp_alias').equals(yelp_alias)
        print(statement.query)
        cur.execute(statement.query)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance
