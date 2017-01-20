class Statement(object):
    def __init__(self, query):
        self.query = query


class Select(Statement):
    def __init__(self, *args):
        super().__init__(None)
        self.statement = 'SELECT'
        print(args)
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
        self.query = query

    def from_table(self, table_name):
        self.query = '%s FROM %s' % (self.query, table_name)
        return Where(self.query)


class Where(Statement):
    def __init__(self, query):
        super().__init__(query)
        self.query = query

    def where(self, column):
        self.query = '%s WHERE %s' % (self.query, column)
        return Comparator(self.query)

    def and_column(self, column):
        self.query = '%s AND %s' % (self.query, column)
        return Comparator(self.query)


class Comparator(Statement):
    def __init__(self, query):
        super().__init__(query)
        self.query = query

    def equals(self, value):
        self.query = '%s = \'%s\'' % (self.query, value)
        return Where(self.query)
