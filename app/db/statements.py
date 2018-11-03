#
# This is a helper class which helps us to build quick an easy sql statements 
#
from __future__ import annotations
from app.db.helper import needs_dollar_quote
from app.db.model import Model

class Statement(object):
    def __init__(self, query):
        self.query = query


class Select(Statement):
    def __init__(self, *args):
        super().__init__(None)
        self.statement = 'SELECT'
        if args:
            # Setup select statement
            self.query = '%s %s' % (self.statement, ','.join(args))
        else:
            self.query = '%s *' % self.statement

    @classmethod
    def select(cls, *args):
        select = Select(*args)
        return From(select.query)


class From(Statement):
    def __init__(self, query):
        super().__init__(query)

    def from_table(self, table_name) -> Where:
        self.query = '%s FROM %s' % (self.query, table_name)
        return Where(self.query)

class AfterFrom(Statement):
    def __init__(self, query):
        super().__init__(query)

    def where(self, column) -> Comparator:
        self.query = '%s WHERE %s' % (self.query, column)
        return Comparator(self.query)
    
    def left_join(self, cls:Model, columns:list):
        self.query = '%s LEFT JOIN %s' % (self.query, cls.table_name)
        join_string = '%s_ ,' % cls.__name__
        self.query = self.query.replace('SELECT ', 'SELECT %s' % join_string.join(columns))  
        return JoinOn(self.query)

class JoinOn(Statement):
    def __init__(self, query):
        super().__init__(query)

    def on_equals(self, column, value):
        self.query = '%s ON %s = %s' % (self.query, column, value)
        return Where(self.query)

class Where(Statement):
    def __init__(self, query):
        super().__init__(query)

    def where(self, column) -> Comparator:
        self.query = '%s WHERE %s' % (self.query, column)
        return Comparator(self.query)

    # TODO Auslagern in eine Separate Klasse
    def and_column(self, column) -> Comparator:
        self.query = '%s AND %s' % (self.query, column)
        return Comparator(self.query)

    def limit(self, limit=10) -> Where:
        self.query = '%s LIMIT %s' % (self.query, str(limit))
        return Where(self.query)


class Comparator(Statement):
    def __init__(self, query):
        super().__init__(query)

    # TODO sollte ein AND - OR - LIMIT
    def equals(self, value) -> Where:
        self.query = '%s = %s' % (self.query, needs_dollar_quote(value))
        return Where(self.query)

    def like(self, value) -> Where:
        self.query = '%s LIKE %s' % (self.query, needs_dollar_quote(value))
        return Where(self.query)

    def similiar(self, value) -> Where:
        self.query = '%s SIMILIAR TO %s' % (self.query, needs_dollar_quote(value))
        return Where(self.query)

    def posix(self, value) -> Where:
        self.query = '%s ~ \'%s\'' % (self.query, value)
        return Where(self.query)

    def is_null(self) -> Where:
        self.query = '%s IS NULL' % self.query
        return Where(self.query)

    def is_not_null(self) -> Where:
        self.query = '%s IS NOT NULL' % self.query
        return Where(self.query)