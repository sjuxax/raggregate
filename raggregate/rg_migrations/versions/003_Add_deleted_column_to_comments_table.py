from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    comments = Table('comments', meta, autoload=True)
    deletedc = Column('deleted', Boolean, default=True)
    deletedc.create(comments)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    comments = Table('comments', meta, autoload=True)
    comments.c.deleted.drop()
