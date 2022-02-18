from peewee import *
import config

db = PostgresqlDatabase(database=config.db_name, user=config.db_user, password=config.db_password, host=config.db_host,
                        port=config.db_port, autocommit=True, autorollback=True)


class BaseModel(Model):
    class Meta:
        database = db


class Posts(BaseModel):
    id = PrimaryKeyField(column_name='id', primary_key=True, unique=True)
    title = TextField(column_name='title', null=True)
    description = TextField(column_name='description', null=True)
    price_amount = IntegerField(column_name='price_amount', null=True)
    price_currency = TextField(column_name='price_currency', null=True)
    link = TextField(column_name='link', null=True)
    date = DateTimeField(column_name='date', null=True)
    source = TextField(column_name='source', null=True)
    parse_date = DateTimeField(column_name='parse_date', null=True)

    class Meta:
        table_name = 'posts'


class Jobs(BaseModel):
    id = PrimaryKeyField(column_name='id', primary_key=True, unique=True)
    posts_uploaded = IntegerField(column_name='posts_uploaded', null=True)
    posts_update = IntegerField(column_name='posts_update', null=True)
    posts_delete = IntegerField(column_name='posts_delete', null=True)
    errors = IntegerField(column_name='errors', null=True)
    date = DateTimeField(column_name='date', null=True)

    class Meta:
        table_name = 'jobs'


class Errors(BaseModel):
    id = PrimaryKeyField(column_name='id', primary_key=True, unique=True)
    error = TextField(column_name='error', null=True)
    description = TextField(column_name='description', null=True)
    source = TextField(column_name='source', null=True)
    job_id = IntegerField(column_name='job_id', null=True)

    class Meta:
        table_name = 'errors'
