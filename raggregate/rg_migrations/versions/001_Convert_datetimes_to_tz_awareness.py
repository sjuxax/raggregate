from sqlalchemy import *
from migrate import *
from migrate.changeset import *

from raggregate.guid_recipe import GUID

# referring to the models directly, this is "very bad" and sqlalchemy-migrate
# docs will yell at you extensively for doing it. OH well, much easier this way
# for the time being, and this migration is pretty basic so it shouldn't cause
# problems down the road (hopefully).

from raggregate.models import Submission
from raggregate.models import User
from raggregate.models import Comment
from raggregate.models import Vote
from raggregate.models import Epistle
from raggregate.models import Stat

model_list = ['Submission', 'User', 'Comment', 'Vote', 'Epistle', 'Stat']

meta = MetaData()

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    for m in model_list:
        t = eval(m).__table__
        t.metadata = meta
        for col in t.c:
            # modify all DateTime columns to tz awareness
            if type(col.type) == DateTime:
                col.alter(type = DateTime(timezone=True))

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    for m in model_list:
        t = eval(m).__table__
        t.metadata = meta
        for col in t.c:
            # modify all DateTime columns to tz naivety
            if type(col.type) == DateTime:
                col.alter(type = DateTime(timezone=False))
