#
# This is a helper class which helps us to build quick an easy sql statements 
#
from __future__ import annotations
from app.db.helper import needs_dollar_quote

class Statement(object):
    def __init__(self, query, statement):
        self.query = query
        self.statement = statement
    def build(self) -> str:    
        return self.statement + ' ' + self.query

class Select(Statement):
    def __init__(self, *args):
        super().__init__(None, None)
        self.statement = 'SELECT'
        if args:
            # Setup select statement
            cols = list(map(lambda col: '_t_.%s' % col, args))
            self.statement = '%s %s' % (self.statement, ','.join(cols))
        else:
            self.statement = '%s _t_.*' % self.statement
        self.query = ''

    @classmethod
    def select(cls, *args):
        select = Select(*args)
        return From(select.query, select.statement)


class From(Statement):
    def __init__(self, query, statement):
        super().__init__(query, statement)

    def from_table(self, table_name) -> Where:
        # TODO: FIX THAT
        self.query = '%s FROM %s' % (self.query, table_name)
        self.statement = self.statement.replace('_t_', table_name)
        return AfterFrom(self.query, self.statement)

class AfterFrom(Statement):
    def __init__(self, query, statement):
        super().__init__(query, statement)

    def join(self, table:str, columns:list=None, table_name=None) -> JoinOn:
        if table_name:
            self.query = '%s JOIN %s %s' % (self.query, table, table_name)
        else:    
            table_name = table
            self.query = '%s JOIN %s' % (self.query, table)

        return self.__join(columns, table_name=table_name)

    def left_join(self, table:str, columns:list=None, table_name=None) -> JoinOn:
        if table_name:
            self.query = '%s LEFT JOIN %s %s' % (self.query, table, table_name)
        else:    
            table_name = table
            self.query = '%s LEFT JOIN %s' % (self.query, table)

        return self.__join(columns, table_name=table_name)
        
    def __join(self, columns:list=None, table_name=None):
        if columns is not None:
            join_string_map = list(map(lambda col: '%s.%s AS %s_%s' % (table_name, col, table_name, col), columns)) 
            sub_statement = ','.join(join_string_map)  
            self.statement = '%s, %s' % (self.statement, sub_statement)
        return JoinOn(self.query, self.statement)    

    def where(self, column) -> Comparator:
        self.query = '%s WHERE %s' % (self.query, column)
        return Comparator(self.query, self.statement)

    def limit(self, limit=10) -> Where:
        self.query = '%s LIMIT %s' % (self.query, str(limit))
        return Where(self.query, self.statement)    

class JoinOn(Statement):
    def __init__(self, query, statement):
        super().__init__(query, statement)

    def on(self, column) -> JoinComparator:
        self.query = '%s ON %s' % (self.query, column)
        return JoinComparator(self.query, self.statement)

    def and_(self, column) -> JoinComparator:
        self.query = '%s AND %s' % (self.query, column)
        return JoinComparator(self.query, self.statement)

class JoinComparator(Statement):
    def __init__(self, query, statement):
        super().__init__(query, statement)

    def equals(self, value) -> AfterFrom:
        self.query = '%s = %s' % (self.query, value)
        return AfterFrom(self.query, self.statement)


class Where(Statement):
    def __init__(self, query, statement):
        super().__init__(query, statement)

    # TODO Auslagern in eine Separate Klasse
    def and_column(self, column) -> Comparator:
        self.query = '%s AND %s' % (self.query, column)
        return Comparator(self.query, self.statement)

    def limit(self, limit=10) -> Where:
        self.query = '%s LIMIT %s' % (self.query, str(limit))
        return Where(self.query, self.statement)


class Comparator(Statement):
    def __init__(self, query, statement):
        super().__init__(query, statement)

    # TODO sollte ein AND - OR - LIMIT
    def equals(self, value, check_for_qoute=True) -> Where:
        self.query = '%s = %s' % (self.query, needs_dollar_quote(value, check_for_qoute))
        return Where(self.query, self.statement)

    def like(self, value, check_for_qoute=True) -> Where:
        self.query = '%s LIKE %s' % (self.query, needs_dollar_quote(value, check_for_qoute))
        return Where(self.query, self.statement)

    def similiar(self, value, check_for_qoute=True) -> Where:
        self.query = '%s SIMILIAR TO %s' % (self.query, needs_dollar_quote(value, check_for_qoute))
        return Where(self.query, self.statement)

    def posix(self, value) -> Where:
        self.query = '%s ~ \'%s\'' % (self.query, value)
        return Where(self.query, self.statement)

    def is_null(self) -> Where:
        self.query = '%s IS NULL' % self.query
        return Where(self.query, self.statement)

    def is_not_null(self) -> Where:
        self.query = '%s IS NOT NULL' % self.query
        return Where(self.query, self.statement)