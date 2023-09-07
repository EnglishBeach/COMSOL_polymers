from peewee import MySQLDatabase

from peewee import Model,CharField,DateTimeField,datetime, DecimalField,ForeignKeyField
from playhouse.mysql_ext import JSONField

# TODO: do beauty
# to export structure
# pwiz -H localhost -u root -e mysql comsol_solves>structure.py

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
    desc = CharField(100, null=True)
    date = DateTimeField(default=datetime.datetime.now)
    data = JSONField(null=False)

    Ke = DecimalField(max_digits=20, decimal_places=5, default=0)
    KH = DecimalField(max_digits=20, decimal_places=5, default=0)
    Kr = DecimalField(max_digits=20, decimal_places=5, default=0)
    Kdisp = DecimalField(max_digits=20, decimal_places=5, default=0)
    KqH = DecimalField(max_digits=20, decimal_places=5, default=0)
    Ks = DecimalField(max_digits=20, decimal_places=5, default=0)
    Kd = DecimalField(max_digits=20, decimal_places=5, default=0)
    Kc = DecimalField(max_digits=20, decimal_places=5, default=0)
    Kp = DecimalField(max_digits=20, decimal_places=5, default=0)
    KrD = DecimalField(max_digits=20, decimal_places=5, default=0)
    Kph = DecimalField(max_digits=20, decimal_places=5, default=0)
    light = DecimalField(max_digits=20, decimal_places=5, default=0)

    class Meta:
        table_name = 'solve'


# FIXME: update not delete
if __name__ == '__main__':
    with db:
        tables = [Solve]
        db.drop_tables(tables)
        db.create_tables(tables)
