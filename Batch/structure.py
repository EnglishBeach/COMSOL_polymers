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
    desc = CharField(100, null=True)
    date = DateTimeField(default=datetime.datetime.now)
    data = JSONField(null=False)

    ke = DecimalField(max_digits=20,
                      decimal_places=5,
                      column_name='Ke',
                      default=0)
    kh = DecimalField(max_digits=20,
                      decimal_places=5,
                      column_name='KH',
                      default=0)
    kr = DecimalField(max_digits=20,
                      decimal_places=5,
                      column_name='Kr',
                      default=0)
    kdisp = DecimalField(max_digits=20,
                         decimal_places=5,
                         column_name='Kdisp',
                         default=0)
    kqh = DecimalField(max_digits=20,
                       decimal_places=5,
                       column_name='KqH',
                       default=0)
    ks = DecimalField(max_digits=20,
                      decimal_places=5,
                      column_name='Ks',
                      default=0)
    kd = DecimalField(max_digits=20,
                      decimal_places=5,
                      column_name='Kd',
                      default=0)
    kc = DecimalField(max_digits=20,
                      decimal_places=5,
                      column_name='Kc',
                      default=0)
    kp = DecimalField(max_digits=20,
                      decimal_places=5,
                      column_name='Kp',
                      default=0)
    krd = DecimalField(max_digits=20,
                       decimal_places=5,
                       column_name='KrD',
                       default=0)
    kph = DecimalField(max_digits=20,
                       decimal_places=5,
                       column_name='Kph',
                       default=0)
    light = DecimalField(max_digits=20,
                         decimal_places=5,
                         column_name='light',
                         default=100)

    class Meta:
        table_name = 'solve'

# FIXME: update not delete
if __name__ == '__main__':
    with db:
        tables = [Solve]
        db.drop_tables(tables)
        db.create_tables(tables)
