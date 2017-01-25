import uuid as UUID
import db.connection as db_con

from db.model import Model
from db.statements import Select


class LocationCategory(Model):
    def __init__(self,
                 uuid=None,
                 location_uuid=None,
                 category_uuid=None):
        self.location_uuid = location_uuid
        self.category_uuid = category_uuid
        self.uuid = uuid
        if not self.uuid:
            self.uuid = str(UUID.uuid4())

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
