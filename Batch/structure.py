from peewee import MySQLDatabase

from peewee import Model,CharField,DateTimeField,datetime, DecimalField,ForeignKeyField
from playhouse.mysql_ext import JSONField

db = MySQLDatabase(
    'comsol_solves',
    user='root',
    password='',
    autoconnect=False,
)


class BaseModel(Model):

    class Meta:
        database = db


class Solve(BaseModel):
    name = CharField(20)
    date = DateTimeField(default=datetime.datetime.now)
    desc = CharField(100, null=True)
    data = JSONField(null=False)


class Const(BaseModel):
    solve = ForeignKeyField(
        Solve,
        related_name='fk_solves',
        on_delete='cascade',
        on_update='cascade',
    )
    name = CharField(10)
    value = DecimalField(max_digits=20,decimal_places=5)




if __name__ == '__main__':
    with db:
        tables = [Const, Solve]
        db.drop_tables(tables)
        db.create_tables(tables)
