from peewee import MySQLDatabase

from peewee import Model,CharField,DateTimeField,datetime, DecimalField,ForeignKeyField
from playhouse.mysql_ext import JSONField

database_connection = MySQLDatabase(
    'comsol_solves',
    user='root',
    password='',
    autoconnect=False,
)


class BaseModel(Model):

    class Meta:
        database = database_connection


class Solve(BaseModel):
    name = CharField(20)
    date = DateTimeField(default=datetime.datetime.now)
    desc = CharField(100, null=True)


class Const(BaseModel):
    solve = ForeignKeyField(
        Solve,
        related_name='fk_solves',
        on_delete='cascade',
        on_update='cascade',
    )
    name = CharField(10)
    value = DecimalField(max_digits=20,decimal_places=5)


class FuncData(BaseModel):

    solve = ForeignKeyField(
        Solve,
        related_name='fk_solves',
        on_delete='cascade',
        on_update='cascade',
    )
    data = JSONField(null=False)


if __name__ == '__main__':
    with database_connection:
        tables = [Const, FuncData, Solve]
        database_connection.drop_tables(tables)
        database_connection.create_tables(tables)
