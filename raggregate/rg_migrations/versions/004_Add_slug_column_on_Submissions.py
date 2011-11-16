from sqlalchemy import *
from migrate import *
from migrate.changeset.constraint import UniqueConstraint

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    submissions = Table('submissions', meta, autoload=True)
    slugc = Column('slug', UnicodeText)
    slugc.create(submissions)
    slugu = UniqueConstraint(slugc)
    slugu.create()
    # do this after upgrade to populate table
    # sqlalchemy-migrate should be extended with a post-upgrade function
    # I intend to do that soon but for now, just run this somewhere else.
    # or replicate the functionality with SQL.
    #for s in db.query(Submission).all():
    #    s.slug = u"{title}-{uuid_first_octet}".format(slugify.slugify(s.title)[:15], str(s.id)[:8])
    #    db.add(s)
    #db.commit()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    submissions = Table('submissions', meta, autoload=True)
    slugu = UniqueConstraint(submissions.c.slug)
    slugu.drop()
    submissions.c.slug.drop()
