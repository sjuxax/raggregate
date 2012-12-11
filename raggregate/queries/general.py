from raggregate.models.stat import Stat

from datetime import datetime
from datetime import timedelta
import calendar
import pytz
import time
import sqlahelper
import sqlalchemy
import json

dbsession = sqlahelper.get_session()

def get_from_post(post, key):
    if key in post and post[key] != '':
        return post[key]
    else:
        return None

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

def find_by_id(id):
    # @FIXME: make these exceptions specific to the case
    # where they can run successfully but do not find
    # the thing we are looking for. This should be really
    # easy as I think we just need NoResultFound.
    from raggregate.queries import submission
    from raggregate.queries import users
    from raggregate.queries import epistle as epistle_queries

    try:
        return submission.get_story_by_id(id)
    except:
        pass

    if users.get_user_by_id(id):
        return users.get_user_by_id(id)

    try:
        return submission.get_comment_by_id(id)
    except:
        pass

    try:
        return epistle_queries.get_epistle_by_id(id)
    except:
        raise

def anon_allow(permission):
    from raggregate.models.anonallowance import AnonAllowance
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
    from raggregate.models.ban import Ban
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

def unroll_sqlalchemy_id_tuple(tup):
    """ If we get a list of IDs from SqlAlchemy, it looks like:
    [(UUID('fake-uuid')), (UUID('fake-uuid-2'))]
    which we almost never want. As such, we have created this utility
    function to change that into:
    [UUID('fake-uuid'), UUID('fake-uuid-2')]
    """
    ret = []

    if len(tup) == 0:
        return []

    for t in tup:
        ret.append(t[0])

    return ret

def gen_uuid():
    import uuid
    import os
    return uuid.UUID(bytes=os.urandom(16))

def check_notify_default(user_id, request):
    #@TODO: make and check user preference for default notify
    # for now we are only going off server settings.
    s = request.registry.settings
    k = 'site.register_notify_by_default'
    if k in s and s[k] == 'true':
        return True
    else:
        return False
