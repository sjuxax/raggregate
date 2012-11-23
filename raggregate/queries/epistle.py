import sqlalchemy
import sqlahelper
from raggregate.queries import users
from raggregate.models.comment import Comment
from raggregate.models.epistle import Epistle

dbsession = sqlahelper.get_session()

def get_epistle_by_sender_id(id):
    return dbsession.query(Epistle).filter(Epistle.sender == id).all()

def get_epistle_by_sender_name(name):
    user = users.get_user_by_name(name)
    return get_epistle_by_sender_id(user.id)

def get_epistle_by_recipient_id(id):
    return dbsession.query(Epistle).filter(Epistle.recipient == id).all()

def get_epistle_by_recipient_name(name):
    user = users.get_user_by_name(name)
    return get_epistle_by_recipient_id(user.id)

def get_new_message_num(id):
    user = users.get_user_by_id(id)
    epistle_num = dbsession.query(Epistle).filter(user.id == Epistle.recipient).filter(Epistle.unread == True).count()
    comment_num = dbsession.query(Comment).filter(sqlalchemy.and_(user.id == Comment.in_reply_to, user.id != Comment.user_id)).filter(Comment.unread == True).count()
    return epistle_num + comment_num

def get_epistle_by_id(id):
    return dbsession.query(Epistle).filter(Epistle.id == id).one()

def mark_epistle_read(e):
    if e.unread == True:
        e.unread = False
        dbsession.add(e)
    return e

def get_unread_epistles_by_recipient_id(id):
    return dbsession.query(Epistle).filter(Epistle.recipient == id).filter(Epistle.unread == True).all()

def get_epistle_roots(id = None, target = 'recipient', include_read = False):
    if not id:
        return "Sorry, you have to provide a valid ID."

    q = dbsession.query(Epistle).filter(sqlalchemy.or_(sqlalchemy.and_(Epistle.parent_type == 'epistle', Epistle.parent == None), Epistle.parent_type != 'epistle'))

    if target == 'sender' or target == 'out':
        q = q.filter(Epistle.sender == id).filter(Epistle.parent_type == 'epistle')
        include_read = True
    else:
        q = q.filter(Epistle.recipient == id)

    if target == 'read':
        include_read = True

    if not include_read:
        q = q.filter(Epistle.unread == True)

    return q.order_by(Epistle.added_on.desc()).all()

def get_epistle_children(id, recursive = True):
    """
    Get the children (replies) of the given epistle id.
    Recursive mode is likely murderous to the database, someone should make it better.
    @param id: id of parent epistle
    @param recursive: recurse down to all children if True (default True)
    """
    all_ep = []
    ep = dbsession.query(Epistle).filter(Epistle.parent == id).all()
    for e in ep:
        all_ep.append(e)
        get_epistle_children(e.id)
    return all_ep

def get_unread_comments_by_user_id(id):
    return dbsession.query(Comment).filter(sqlalchemy.and_(Comment.unread == True, Comment.in_reply_to == id, Comment.user_id != id)).all()

def get_read_comments_by_user_id(id):
    return dbsession.query(Comment).filter(Comment.in_reply_to == id).order_by(Comment.added_on.desc()).limit(20).all()

def mark_comment_read(c):
    if c.unread == True:
        c.unread = False
        dbsession.add(c)
    return c
