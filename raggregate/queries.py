from raggregate.models import DBSession
from raggregate.models.user import User
from raggregate.models.vote import Vote
from raggregate.models.submission import Submission
from raggregate.models.comment import Comment
from raggregate.models.epistle import Epistle
from raggregate.models.stat import Stat
from raggregate.models.ban import Ban
from raggregate.new_queries import users

from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
import sqlalchemy

import sqlahelper

from beaker import cache

import uuid
import os

from raggregate.login_adapters import LoginAdapterExc

from datetime import datetime
from datetime import timedelta
import calendar

import math

import json

import time

import pytz

dbsession = sqlahelper.get_session()

#one day, we should break this into files instead of sections

def realize_timedelta_constructor(con_str):
    """ Converts a timedelta constructor parameter list into a real timedelta.
    @param con_str: the constructor parameters to convert"""
    return eval("timedelta({0})".format(con_str))

def now_in_utc():
    return datetime.utcnow().replace(tzinfo=pytz.utc)

def get_key_from_stat(key, type = None):
    sa = dbsession.query(Stat).filter(Stat.key == key).one()
    val = json.loads(sa.value)

    if type == 'datetime':
        val = datetime.fromtimestamp(val).replace(tzinfo=pytz.utc)

    return {'key': key, 'value': val, 'sa': sa}

def set_key_in_stat(key, value, type = None):

    if type == 'datetime':
        value = calendar.timegm(time.gmtime(time.mktime(value.timetuple())))

    try:
        sa = dbsession.query(Stat).filter(Stat.key == key).one()
        sa.key = key
        sa.value = value
    except sqlalchemy.orm.exc.NoResultFound:
        sa = Stat(key = key, value = json.dumps(value))

    dbsession.add(sa)
    dbsession.flush()
    return 0

def count_sa_obj(obj):
    """
    Accept an SA query object and append .count() to tally the total applicable number.
    This is used to tell if we need pagination controls.
    @param obj: a Sqlalchemy query object
    @return: an integer representing the potential number of rows
    """
    return obj.count()

#epistles
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

#scary/inefficient general queries, using for readibility/clarity, optimize anything important

def find_by_id(id):
    try:
        return get_story_by_id(id)
    except:
        pass

    if users.get_user_by_id(id):
        return users.get_user_by_id(id)

    try:
        return get_comment_by_id(id)
    except:
        pass

    try:
        return get_epistle_by_id(id)
    except:
        raise

def anon_allow(permission):
    try:
        dbsession.query(AnonAllowance).filter(AnonAllowance.permission == permission).filter(AnonAllowance.allowed == True).one()
        return True
    except sqlalchemy.orm.exc.NoResultFound:
        return False

def strip_p_tags(s):
    s = s.replace('<p>', '')
    s = s.replace('</p>', '')
    return s

def strip_all_html(s):
    if s == '' or s == None or not s:
        return s
    from lxml.html import fromstring, tostring
    lx = fromstring(s)
    return tostring(lx, method="text", encoding="unicode")

def list_bans(ip = None, username = None, active = True):
    # if ip or username are specified, search and see if we have any current bans for these.
    if not active:
        bans_q = dbsession.query(Ban)
    else:
        bans_q = dbsession.query(Ban).filter(Ban.expires > datetime.utcnow())

    if ip:
        bans = bans_q.filter(Ban.ip == ip).all()
        if len(bans) > 0:
            return True
        else:
            return False

    if username:
        bans = bans_q.filter(Ban.username == username).all()
        if len(bans) > 0:
            return True
        else:
            return False

    # if nothing is specified, just return all bans.
    # @TODO: make this work with the active keyword mentioned yonder
    # should work now but we use this to return every ban ever issued
    # presently, so would need to change behavior on front-end
    return dbsession.query(Ban).all()

