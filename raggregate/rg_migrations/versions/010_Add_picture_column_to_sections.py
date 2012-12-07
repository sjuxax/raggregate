from sqlalchemy import *
from migrate import *
from raggregate.guid_recipe import GUID


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    sections = Table('sections', meta, autoload=True)
    section_pictures = Table('section_pictures', meta, autoload=True)
    picture_c = Column('picture', GUID, ForeignKey('section_pictures.id'))
    picture_c.create(sections)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    sections = Table('sections', meta, autoload=True)
    sections.c.picture.drop()
