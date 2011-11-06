from sqlalchemy import *
from migrate import *
from raggregate.guid_recipe import GUID

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    comments = Table('comments', meta, autoload=True)
    unreadc = Column('unread', Boolean, default=True)
    in_reply_toc = Column('in_reply_to', GUID, nullable=True)
    unreadc.create(comments)
    in_reply_toc.create(comments)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    comments = Table('comments', meta, autoload=True)
    comments.c.unread.drop()
    comments.c.in_reply_to.drop()
