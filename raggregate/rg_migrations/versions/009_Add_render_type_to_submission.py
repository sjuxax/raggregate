from sqlalchemy import *
from migrate import *
from migrate.changeset.constraint import UniqueConstraint

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    submissions = Table('submissions', meta, autoload=True)
    render_typec = Column('render_type', UnicodeText, default=u"story_md")
    render_typec.create(submissions)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    submissions = Table('submissions', meta, autoload=True)
    submissions.c.render_type.drop()
