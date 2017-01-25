import uuid as UUID
import regex
import db.connection as db_con
from db.statements import Select
from psycopg2.extensions import AsIs


class Model(object):
    class_name = None

    def __init__(self, created_at=None, modified_at=None, uuid=None, **entries):
        self.created_at = created_at
        self.modified_at = modified_at
        self.uuid = uuid
        if not self.uuid:
            self.uuid = str(UUID.uuid4())
        self.__dict__.update(entries)

    def insert(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        insert_statement = 'INSERT INTO %s (' + ', '.join(self.attrs().keys()) + ') VALUES (' + ', '.join((['%s'] * len(self.attrs().keys()))) + ')'
        values = list(self.attrs().values())
        values.insert(0, AsIs(self.table_name()))
        cur.execute(insert_statement, tuple(values))

        con.commit()
        cur.close()
        con.close()

    def excluded_atts(self):
        return ['created_at', 'modified_at']

    def attrs(self):
        attrs_dict = self.__dict__
        wanted_keys = list(k for k in attrs_dict.keys() if k not in self.excluded_atts())
        attrs_dict = dict((k, v) for k, v in attrs_dict.items() if k in wanted_keys)
        return attrs_dict

    @classmethod
    def table_name(cls):
        if cls.class_name is None:
            cls.class_name = regex.findall(r'[A-Z][a-z]+', cls.__name__)
            cls.class_name = '_'.join(cls.class_name).lower()
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

    @classmethod
    def delete_all(cls):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('DELETE FROM %s', (AsIs(cls.table_name()),))

        con.commit()
        cur.close()
        con.close()
