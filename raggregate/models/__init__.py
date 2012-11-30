import transaction

import sqlalchemy

from raggregate.guid_recipe import GUID

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from sqlalchemy.event import listen

from sqlalchemy.schema import Table

from zope.sqlalchemy import ZopeTransactionExtension

import cryptacular.bcrypt

import uuid
import os

import sqlahelper

DBSession = sqlahelper.get_session()
Base = declarative_base()

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()


#def populate():
#    session = DBSession()
#    model = MyModel(name=u'root', value=55)
#    session.add(model)
#    session.flush()
#    transaction.commit()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    listen(sqlalchemy.orm.mapper, 'before_insert', make_uuid)
#    try:
#        populate()
#    except IntegrityError:
#        transaction.abort()

def initialize_sql_test(engine):
    DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    listen(sqlalchemy.orm.mapper, 'before_insert', make_uuid)
    return [DBSession, Base]
#    try:
#        populate()
#    except IntegrityError:
#        transaction.abort()

def make_uuid(mapper, connection, target):
    if hasattr(target, 'id') and target.id is None:
        if type(mapper.columns.get('id').type) is GUID:
            target.id = uuid.UUID(bytes=os.urandom(16))
