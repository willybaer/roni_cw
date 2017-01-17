import uuid
import regex
import db.connection as db_con
from db.statements import Select


class Model(object):
    class_name = None

    def __init__(self, created_at=None, modified_at=None, uuid=str(uuid.uuid4()), **entries):
        self.created_at = created_at
        self.modified_at = modified_at
        self.uuid = uuid
        self.__dict__.update(entries)

    @classmethod
    def table_name(cls):
        if cls.class_name is None:
            cls.class_name = regex.findall(r'[A-Z][a-z]+', cls.__name__)
            cls.class_name = ('%s_%s' % (db_con.TABLE_NAME_PREFIX, '_'.join(cls.class_name).lower()))
        return cls.class_name

    @classmethod
    def find_all(cls):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = Select.select().from_table(cls.table_name())
        print(statement.query)
        cur.execute(statement.query)

        # For each entry create a new instance
        entries = cur.fetchall()
        model_instances = []
        for entry in entries:
            m = cls(**entry)
            model_instances.append(m)

        cur.close()
        con.close()

        return model_instances

