from sqlalchemy import *
from migrate import *
from raggregate.guid_recipe import GUID

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    votes = Table('votes', meta, autoload=True)
    motdc = Column('motd_id', GUID)
    motdc.create(votes)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    votes = Table('votes', meta, autoload=True)
    votes.c.motd_id.drop()
