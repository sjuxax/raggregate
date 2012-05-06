from sqlalchemy import *
from migrate import *

from raggregate.guid_recipe import GUID

meta = MetaData()

def make_sections_table(meta):
    users = Table('users', meta, autoload=True)

    sections = Table(
        'sections', meta,
        Column('id', GUID, primary_key=True),
        Column('name', UnicodeText),
        Column('description', UnicodeText),
        Column('subscribe_by_default', Boolean),
        Column('parent', GUID, ForeignKey('sections.id'), nullable=True),
        Column('added_by', GUID, ForeignKey('users.id'), nullable=False),
        Column('enabled', Boolean, default=True),
        Column('added_on', DateTime(timezone=True), default=sqlalchemy.sql.func.now()),
        Column('modified_on', DateTime(timezone=True), default=sqlalchemy.sql.func.now()),
    )
    return sections

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    sections = make_sections_table(meta)
    sections.create()
    submissions = Table('submissions', meta, autoload=True)
    sectionc = Column('section', GUID, ForeignKey('sections.id'), nullable=True)
    sectionc.create(submissions)

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    sections = make_sections_table(meta)
    submissions = Table('submissions', meta, autoload=True)
    submissions.c.section.drop()
    sections.drop()
