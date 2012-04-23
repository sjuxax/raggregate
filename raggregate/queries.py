from raggregate.models import DBSession
from raggregate.models.user import User
from raggregate.models.vote import Vote
from raggregate.models.submission import Submission
from raggregate.models.comment import Comment
from raggregate.models.epistle import Epistle
from raggregate.models.stat import Stat
from raggregate.models.ban import Ban

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

#users
def get_user_by_id(id):
    try:
        return dbsession.query(User).filter(User.id == id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

def get_user_by_name(name):
    return dbsession.query(User).filter(User.name == name).one()

def is_user_allowed_admin_action(user_id, target_id, request = None, target_class = 'user_post',):
    """
    @param user_id: the user id of the person initiating the request
    @param target_id: the id of the item the person is attempting to act upon
    @param request: optional request passed to query for session info etc
    @param target_class: optional class of item being targeted
    """
    allow = False

    if user_id is None:
        return None

    u = get_user_by_id(user_id)

    # instantly grant whatever action this is to the admin
    try:
        if u.is_user_admin():
            return True

        if target_class == 'user_post':
            target = find_by_id(target_id)
            if type(target) == Comment or type(target) == Submission:
                allow = (str(target.submitter.id) == user_id)
        elif target_class == 'user_info':
            allow = (str(target_id) == str(user_id))
    except:
        # always return False in case of exception.
        pass

    return allow

def get_followed_users(id):
    """
    Get a list of IDs of followed users. We may want to inject this into the session.
    @param id: user id whose followed users we want to find
    @return: list of UUIDs for followed users
    """
    u = get_user_by_id(id)
    follow_list = u.follows
    ret = {}
    for f in follow_list:
        ret[f.id] = f
    return ret

def get_user_votes_on_submission(user_id, submission_id):
    #@TODO: make this agnostic, work on comments too
    vote_dict = {}
    vs = dbsession.query(Vote).filter(Vote.user_id == user_id).filter(Vote.submission_id == submission_id).filter(Vote.comment_id == None).all()
    for v in vs:
        if v.submission_id not in vote_dict:
            vote_dict[v.submission_id] = []
        vote_dict[v.submission_id].append(v.direction)
    return vote_dict

def get_user_votes_on_all_submissions(user_id):
    #@TODO: make this agnostic, work on comments too
    vote_dict = {}
    vs = dbsession.query(Vote).filter(Vote.user_id == user_id).filter(Vote.comment_id == None).all()
    for v in vs:
        if v.submission_id not in vote_dict:
            vote_dict[v.submission_id] = []
        vote_dict[v.submission_id].append(v.direction)
    return vote_dict

def get_user_votes_on_submissions_comments(user_id, submission_id):
    #@TODO: merge this into function above since logic is almost identical
    vote_dict = {}
    vs = dbsession.query(Vote).filter(Vote.user_id == user_id).filter(Vote.submission_id == submission_id).filter(Vote.comment_id != None).all()
    for v in vs:
        if v.comment_id not in vote_dict:
            vote_dict[v.comment_id] = []
        vote_dict[v.comment_id].append(v.direction)
    return vote_dict

def create_temp_user(initial_pw = None):
    # cryptacular will not accept \x00 in passwords
    # so if we generate that, we should try again
    # UUID doesn't care about this afaik; if we get bugs
    # like "TypeError: must be string without null bytes..."
    # after this fix, we should scrutinize other stuff that
    # uses os.urandom.
    count = 0
    pw_null = True
    while pw_null:
        if initial_pw and count == 0:
            pw = initial_pw
        else:
            pw = os.urandom(8)
        if '\x00' not in pw:
            pw_null = False
        count += 1
    return User("{0}".format(uuid.UUID(bytes=os.urandom(16))), pw, real_name = "Unregistered User", temporary = True)

def fuzzify_date(d):
    # requires py-pretty, which I think is unmaintained. Its Google Code page is offline.
    # we should change this to use something better later, probably an adaptation of
    # django's timesince.py, because there are no apparently no other good general libraries
    # that provide this.
    from raggregate import pretty
    return pretty.date(d)

def create_user(**kwargs):
    # @TODO: we should make this accept arbitrary kwargs that map to the u object
    # instead of only allowing explicit setting below. That would take significant
    # reworking of this function.
    # Typical usage:
    # create_user(origination=x, username=un, password=pn, remote_object if relevant)

    # also used for temp -> permanent usership
    if 'temp_to_perm' in kwargs and kwargs['temp_to_perm'] == True:
        u = get_user_by_id(kwargs['extant_id'])
    else:
        u = create_temp_user()

    if 'origination' in kwargs:
        o = kwargs['origination']
    else:
        o = 'site'

    if 'just_temp' in kwargs and kwargs['just_temp'] == True:
        # everything we need for this is covered in create_temp_user
        return u

    if 'picture' in kwargs:
        u.picture = kwargs['picture']

    # user is permanent, mark the universal information
    u.name = kwargs['username']
    u.temporary = False
    u.real_name = None

    if o == 'site':
        u.password = u.hash_pw(kwargs['password'])
    elif o == 'twitter':
        # we do not need to change from the random password generated in the temp object
        # for twitter authorization; if twitter says the user is good, we assume it is so.
        u.twitter_origination = True
        u.twitter_oauth_key = kwargs['remote_object']['oauth_token']
        u.twitter_oauth_secret = kwargs['remote_object']['oauth_token_secret']
        u.real_name = kwargs['remote_object']['screen_name']
    elif o == 'facebook':
        # we do not need to change from the random password generated in the temp object
        # for facebook authorization; if facebook says the user is good, we assume it is so.
        u.facebook_origination = True
        u.facebook_user_id = kwargs['remote_object']['id']
        u.real_name = kwargs['remote_object']['name']

    dbsession.add(u)
    dbsession.flush()

    return u

def login_user(request, u, password, bypass_password = False):
    # check a user's password and log in if correct
    s = request.session
    good_login = False

    if password is not None and u.verify_pw(password):
        good_login = True

    if bypass_password:
        # assume validation has occurred elsewhere
        # i.e., in twitter or facebook login processes
        good_login = True

    if good_login:
        s['users.id'] = str(u.id)
        s['users.display_name'] = u.display_name()
        s['logged_in'] = True
        return True
    else:
        raise LoginAdapterExc("Invalid login information.")
        return False

def add_user_picture(orig_filename, new_prefix, up_dir, image_file):
    import time
    import os
    import tempfile

    new_filename = "{0}-{1}.jpg".format(new_prefix, time.time())

    full_path = os.path.join(up_dir, new_filename)

    import hashlib
    skip_seek = False

    try:
        image_file.seek(0)
    except AttributeError:
        # we want a file, so if this isn't a file, make one.
        tmp_f = tempfile.TemporaryFile()
        # urllib2.urlopen object passed, read is implemented
        # or maybe not, and then just assume the string is the binary data
        # and ready to be written directly
        if hasattr(image_file, 'read'):
            # im_b for "image binary"
            im_b = image_file.read()
        else:
            im_b = image_file
        tmp_f.write(im_b)
        image_file = tmp_f

    image_file.seek(0)
    sha = hashlib.sha1()
    sha.update(image_file.read())
    sha = sha.hexdigest()

    if not skip_seek:
        image_file.seek(0)
    f = image_file
    from PIL import Image
    im = Image.open(f)
    im.thumbnail((50, 50), Image.ANTIALIAS)

    im.save(full_path, 'JPEG')

    from raggregate.models.user import UserPicture
    up = UserPicture(orig_filename, new_filename, sha, 0)
    dbsession.add(up)
    dbsession.flush()
    return up.id

#epistles
def get_epistle_by_sender_id(id):
    return dbsession.query(Epistle).filter(Epistle.sender == id).all()

def get_epistle_by_sender_name(name):
    user = get_user_by_name(name)
    return get_epistle_by_sender_id(user.id)

def get_epistle_by_recipient_id(id):
    return dbsession.query(Epistle).filter(Epistle.recipient == id).all()

def get_epistle_by_recipient_name(name):
    user = get_user_by_name(name)
    return get_epistle_by_recipient_id(user.id)

def get_new_message_num(id):
    user = get_user_by_id(id)
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

    if get_user_by_id(id):
        return get_user_by_id(id)

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

