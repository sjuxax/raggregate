from sqlalchemy import *
from sqlalchemy import orm
from migrate import *

from raggregate.models import Comment

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    smaker = orm.sessionmaker(bind=migrate_engine)
    db = smaker()
    comments = Table('comments', meta, autoload=True)
    deletedc = Column('deleted', Boolean, default=False)
    deletedc.create(comments)
    print "Updating deleted flag on existing comments..."
    for c in db.query(Comment).all():
        if c.body == '[deleted]':
            c.deleted = True
            db.add(c)
    db.commit()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    comments = Table('comments', meta, autoload=True)
    comments.c.deleted.drop()
