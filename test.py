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

class Const(BaseModel):
    name = CharField()
    solve = ForeignKeyField(column_name='solve_id', field='id', model=Solve)
    value = DecimalField()

    class Meta:
        table_name = 'const'

