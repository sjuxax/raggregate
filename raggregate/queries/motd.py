import sqlalchemy
import sqlahelper
import random
from raggregate.models import DBSession
from raggregate.models.motd import MOTD
from raggregate.queries import general

dbsession = sqlahelper.get_session()

def create_motd(message = None, author = None, source = None,
        link = None, added_by = None, datestring = None):

    new_motd = MOTD(message = message, author = author, source = source,
            link = link, added_by = added_by, datestring = datestring)

    dbsession.add(new_motd)
    dbsession.flush()
    return new_motd

def get_message_by_id(id):
    try:
        return dbsession.query(MOTD).filter(MOTD.id == id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

def get_random_message():
    messages = dbsession.query(MOTD.id).all()
    if len(messages) > 0:
        return get_message_by_id(random.choice(general.unroll_sqlalchemy_id_tuple(messages)))
    else:
        return None

def get_all_messages():
    return dbsession.query(MOTD).all()
