from peewee import *

database = MySQLDatabase('comsol_solves', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': 'localhost', 'user': 'root'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Solve(BaseModel):
    kh = DecimalField(column_name='KH', null=True)
    data = TextField()
    date = DateTimeField()
    desc = CharField(null=True)
    name = CharField()

    class Meta:
        table_name = 'solve'


if __name__ == '__main__':
    with db:
        tables = [Const, Solve]
        db.drop_tables(tables)
        db.create_tables(tables)
