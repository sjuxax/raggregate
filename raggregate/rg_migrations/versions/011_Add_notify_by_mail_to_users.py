from sqlalchemy import *
from migrate import *
from raggregate.guid_recipe import GUID


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    users = Table('users', meta, autoload=True)
    notify_by_mailc = Column('notify_by_mail', Boolean, default=True)
    notify_by_mailc.create(users)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    users = Table('users', meta, autoload=True)
    users.c.notify_by_mail.drop()
