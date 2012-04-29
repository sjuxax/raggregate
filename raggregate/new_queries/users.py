from raggregate.models import DBSession
from raggregate.models.user import User
from raggregate.models.submission import Submission
from raggregate.models.vote import Vote
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
#from raggregate import queries
import sqlalchemy
import uuid
import sqlahelper

dbsession = sqlahelper.get_session()

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
