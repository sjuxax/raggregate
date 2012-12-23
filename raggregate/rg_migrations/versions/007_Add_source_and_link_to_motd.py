from sqlalchemy import *
from migrate import *
from migrate.changeset.constraint import UniqueConstraint

def upgrade(migrate_engine):
    print "no-op"
    return True


def downgrade(migrate_engine):
    print "no-op"
    return True
