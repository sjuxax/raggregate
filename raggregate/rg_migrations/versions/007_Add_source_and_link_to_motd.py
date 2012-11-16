from sqlalchemy import *
from migrate import *
from migrate.changeset.constraint import UniqueConstraint

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    motd = Table('motd', meta, autoload=True)
    sourcec = Column('source', UnicodeText)
    sourcec.create(motd)
    linkc = Column('link', UnicodeText)
    linkc.create(motd)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    motd = Table('motd', meta, autoload=True)
    motd.c.source.drop()
    motd.c.link.drop()
