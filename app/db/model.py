import uuid as UUID
import regex
import app.db.connection as db_con

from app.db.statements import Select
from psycopg2.extensions import AsIs
from app.db.helper import needs_dollar_quote


class Model(Select):
    class_name = None

    def __init__(self, created_at=None, modified_at=None, uuid=None, **entries):
        self._created_at = created_at
        self._modified_at = modified_at
        self._uuid = uuid
        if not self._uuid:
            self._uuid = str(UUID.uuid4())
        self.__dict__.update(entries)

    @property
    def created_at(self):
        return self._created_at

    @property
    def modified_at(self):
        return self._modified_at

    @property
    def uuid(self):
        return self._uuid
        
    #
    # Insert 
    #
    def insert_statement(self):
        return 'INSERT INTO %s (' + ', '.join(self.attrs().keys()) + ') VALUES (' + ', '.join(
            (['%s'] * len(self.attrs().keys()))) + ')'

    def insert_values(self):
        values = list(self.attrs().values())
        values.insert(0, AsIs(self.table_name()))
        return tuple(values)

    def insert(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute(self.insert_statement(), self.insert_values())
        con.commit()

        cur.close()
        con.close()

    #
    # Update
    #
    def update_statement(self):
        keys = list(filter(lambda x: x != 'uuid', self.attrs().keys()))
        keys = list(map(lambda x: x + ' = %s', keys))
        return 'UPDATE %s SET ' + ', '.join(keys) + 'WHERE uuid = %s' # TODO: UUID als decorator definieren

    def update_values(self):
        values = list(filter(lambda x: x != self.uuid, self.attrs().values()))
        values.insert(0, AsIs(self.table_name()))
        values.append(self.uuid) # TODO: UUID als decorator definieren
        return tuple(values)

    def update(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute(self.update_statement(), self.update_values())
        con.commit()
        
        cur.close()
        con.close()    

    @staticmethod
    def excluded_atts():
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

    #
    # Find 
    #
    @classmethod
    def find(cls, uuid):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()).where('uuid').equals(uuid) # TODO: 
        print(statement.query)
        cur.execute(statement.query)

        # For each entry create a new instance
        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance


    #
    # Delete
    #
    @classmethod
    def delete_all(cls):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute('DELETE FROM %s', (AsIs(cls.table_name()),))

        con.commit()
        cur.close()
        con.close()
