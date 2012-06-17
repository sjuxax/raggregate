from sqlalchemy import *
from migrate import *

from raggregate.guid_recipe import GUID

meta = MetaData()

def make_subscriptions_table(meta):
    users = Table('users', meta, autoload=True)
    sections = Table('sections', meta, autoload=True)

    users_subscriptions = Table(
        'users_subscriptions', meta,
        Column('id', GUID, primary_key=True),
        Column('user_id', GUID, ForeignKey('users.id')),
        Column('section_id', GUID, ForeignKey('sections.id')),
        Column('subscription_status', Boolean),
    )
    return users_subscriptions

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    subscriptions = make_subscriptions_table(meta)
    subscriptions.create()

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    subscriptions = make_subscriptions_table(meta)
    subscriptions.drop()
