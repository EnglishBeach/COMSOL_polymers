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


class Solves(BaseModel):
    name = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    description = CharField(100, null=True)


class Consts(BaseModel):
    solve = ForeignKeyField(
        Solves,
        related_name='fk_solves',
        on_delete='cascade',
        on_update='cascade',
    )
    key = CharField(10)
    value = DecimalField()


class Functions(BaseModel):

    solve = ForeignKeyField(
        Solves,
        related_name='fk_solves',
        on_delete='cascade',
        on_update='cascade',
    )
    data = JSONField(null=False)
    # time = DecimalField()
    # value = DecimalField()


if __name__ == '__main__':
    with database_connection:
        tables = [Consts, Functions, Solves]
        database_connection.drop_tables(tables)
        database_connection.create_tables(tables)
