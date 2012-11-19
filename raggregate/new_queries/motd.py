import sqlalchemy
import sqlahelper
import random
from raggregate.models import DBSession
from raggregate.models.motd import MOTD
from raggregate import queries

dbsession = sqlahelper.get_session()

def get_message_by_id(id):
    try:
        return dbsession.query(MOTD).filter(MOTD.id == id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

def get_random_message():
    messages = dbsession.query(MOTD.id).all()
    if len(messages) > 0:
        return get_message_by_id(random.choice(queries.unroll_sqlalchemy_id_tuple(messages)))
    else:
        return None

    return get_message_by_id(random.choice(queries.unroll_sqlalchemy_id_tuple(motds)))

def get_all_messages():
    return dbsession.query(MOTD).all()
