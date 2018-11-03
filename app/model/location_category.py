import uuid as UUID
import app.db.connection as db_con

from app.db.model import Model
from app.db.statements import Select


class LocationCategory(Model):
    def __init__(self,
                 location_uuid=None,
                 category_uuid=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.location_uuid = location_uuid
        self.category_uuid = category_uuid

    @classmethod
    def find_by_location_and_category(cls, location_uuid, category_uuid):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = Select.select().from_table(cls.table_name()).where('location_uuid').equals(location_uuid).and_column('category_uuid').equals(category_uuid)
        cur.execute(statement.query)

        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance
