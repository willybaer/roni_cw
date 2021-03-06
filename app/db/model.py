import uuid as UUID
import regex
import app.db.connection as db_con

from datetime import datetime
from app.db.statements import Select
from psycopg2.extensions import AsIs
from app.db.helper import needs_dollar_quote  

class Model(Select):
    class_name:str = None
    created_at: datetime
    modified_at: datetime
    uuid:str

    def __init__(self, uuid=None, created_at=None, modified_at=None, **entries):
        self.created_at = created_at
        self.modified_at = modified_at
        self.uuid = uuid
        if self.uuid is None:
            self.uuid = str(UUID.uuid4())

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

        statement = self.insert_statement()
        values = self.insert_values()
        cur.execute(statement, values)
        con.commit()

        cur.close()
        con.close()

    #
    # Update
    #
    def update_statement(self):
        keys = list(filter(lambda x: x != 'uuid', self.attrs().keys()))
        keys = list(map(lambda x: x + ' = %s', keys))
        return 'UPDATE %s SET ' + ', '.join(keys) + ' WHERE uuid = %s'

    def update_values(self):
        values = list(filter(lambda x: x != self.uuid, self.attrs().values()))
        values.insert(0, AsIs(self.table_name()))
        values.append(self.uuid)
        return tuple(values)

    def update(self):
        con = db_con.connection()
        cur = db_con.cursor(con)

        cur.execute(self.update_statement(), self.update_values())
        con.commit()
        
        cur.close()
        con.close()    

    def excluded_atts(self) -> list:
        return ['created_at', 'modified_at']
    
    def attrs(self):
        excluded = self.excluded_atts()
        attrs_dict = self.__dict__
        wanted_keys = list(k for k in attrs_dict.keys() if k not in excluded)
        attrs_dict = dict((k, v) for k, v in attrs_dict.items() if k in wanted_keys)
        
        wanted_keys = list(map(lambda key: key if len(key.split('__')) < 2 else key.split('__')[1], wanted_keys))
        return dict(zip(wanted_keys, attrs_dict.values()))

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

        statement = cls.select().from_table(cls.table_name()).where('uuid').equals(uuid).build()
        print(statement)
        cur.execute(statement)

        # For each entry create a new instance
        entry = cur.fetchone()
        model_instance = None
        if entry:
            model_instance = cls(**entry)

        cur.close()
        con.close()

        return model_instance

    @classmethod
    def find_with_limit(cls, limit):
        con = db_con.connection()
        cur = db_con.cursor(con)

        statement = cls.select().from_table(cls.table_name()).limit(limit).build()
        print(statement)
        cur.execute(statement)

        # For each entry create a new instance
        entries = cur.fetchall()
        if len(entries) == 0:
            return None

        model_instances = []
        for entry in entries:
            model_instances.append(cls(**entry))

        cur.close()
        con.close()

        return model_instances

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
