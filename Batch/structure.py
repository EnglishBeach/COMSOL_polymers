import peewee as pe

database_connection = pe.MySQLDatabase('comsol_solves',
                                       user='root',
                                       password='',
                                       autoconnect=False)

path = r'D:\WORKS\COMSOL_polymers'

class BaseModel(pe.Model):

    class Meta:
        database = database_connection


class Solves(BaseModel):
    name = pe.CharField()
    date = pe.DateTimeField(default=pe.datetime.datetime.now)
    description = pe.CharField(100)


class Coefs(BaseModel):
    solve = pe.ForeignKeyField(Solves,
                               related_name='fk_solves',
                               on_delete='cascade',
                               on_update='cascade')
    type = pe.CharField(10),
    value = pe.DecimalField()


class Functions(BaseModel):

    # class Meta:
    #     primary_key = False

    solve = pe.ForeignKeyField(Solves,
                               related_name='fk_solves',
                               on_delete='cascade',
                               on_update='cascade')
    name = pe.CharField(10),
    time = pe.DecimalField(),
    value = pe.DecimalField(),


if __name__ == '__main__':
    with database_connection:
        classes = [Solves, Coefs, Functions]
        database_connection.drop_tables(classes)
        database_connection.create_tables(classes)