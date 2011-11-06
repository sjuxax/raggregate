from raggregate.models import DBSession
from raggregate.models import User
from raggregate.models import Vote
from raggregate.models import Submission
from raggregate.models import Comment
from raggregate.models import Epistle
from raggregate.models import Stat
from raggregate.models import Ban

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

def calc_hot_average(hot_point_window = timedelta(hours = 6)):
    """
    Calculate the average point assignment of stories over the last hot_point_window time.
    """
    story_votes = dbsession.query(Vote.submission_id, func.sum(Vote.points).label('points')).filter(Vote.added_on < now_in_utc() and Vote.added_on > (now_in_utc() - hot_point_window)).group_by(Vote.submission_id).all()

    aggregate = 0
    count = 0

    for sv in story_votes:
        aggregate += sv.points
        count += 1

    print "aggregate: " + str(aggregate)
    print "count: " + str(count)

    if aggregate <= 0:
        hot_avg = 0
    else:
        # @TODO: this floating point division is basically extraneous
        # but I want it to look like something is happening for now
        # someone who cares about performance might want to remove this
        # especially since we are just creating an integer further down
        # if this is >= 1, which it will be in most sites.
        # especially since decimal comparison is meaningless here; < 1 = 0
        # users only vote in integers
        hot_avg = float(aggregate) / float(count)

    if hot_avg >= 1.0:
        hot_avg = math.floor(hot_avg)

    set_key_in_stat('hot_avg', hot_avg)
    set_key_in_stat('hot_avg_timestamp', now_in_utc(), type = 'datetime')

    print("hot_avg: {0}".format(hot_avg))

    return hot_avg

def calc_hot_window_score(submission_id, hot_point_window = timedelta(hours = 6)):
    """
    Retrieve vote/score information for a given submission over hot_point_window time.
    Count votes received in the last hot_point_window time. If this is higher than normal,
    the story will be considered hot.

    @param submission_id: the submission to calculate
    @param hot_point_window: timedelta object representing acceptable vote timeframe from now
    """
    try:
        story_votes = dbsession.query(Vote.submission_id, func.sum(Vote.points).label('points')).filter(Vote.added_on < now_in_utc() and Vote.added_on > (now_in_utc() - hot_point_window)).filter(Vote.submission_id == submission_id).group_by(Vote.submission_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        # no votes on this story yet
        return 0

    story = get_story_by_id(submission_id)
    story.hot_window_score = story_votes.points
    story.hot_window_score_timestamp = now_in_utc()
    dbsession.add(story)
    return story_votes.points

def calc_all_hot_window_scores(hot_eligible_age = timedelta(hours = 48)):
    # by default, only stories from the last 48 hours are eligible for "hot" status
    stories = dbsession.query(Submission).filter(Submission.deleted == False).filter(Submission.added_on > (now_in_utc() - hot_eligible_age)).all()

    for s in stories:
        calc_hot_window_score(s.id)

    set_key_in_stat('mass_hot_window_timestamp', now_in_utc(), type = 'datetime')

    dbsession.flush()

    return 0

def recentize_hots(hot_recalc_threshold = timedelta(hours = 1), hot_point_window = None, hot_eligible_age = None):
    """
    Recalculate the hot page every hot_recalc_threshold time.
    This depends on the timestamp keys placed in Stat in other calls.
    """

    count = 0
    def call_hot_average():
        if hot_point_window:
            calc_hot_average(hot_point_window)
        else:
            calc_hot_average()

    def get_hot_avg_time():
        hot_avg_timestamp = None

        try:
            hot_avg_timestamp = get_key_from_stat('hot_avg_timestamp', type = 'datetime')
        except sqlalchemy.orm.exc.NoResultFound:
            call_hot_average()

        if type(hot_avg_timestamp) == dict:
            return hot_avg_timestamp['value']
        else:
            return None

    hot_avg_timestamp = None

    while hot_avg_timestamp == None and count < 5:
        hot_avg_timestamp = get_hot_avg_time()
        count += 1

    if count >= 5:
        print("\t-----WARNING WARNING WARNING-----\n\tSomething has gone tragically wrong with the hotness: AVG.\n\t-----WARNING WARNING WARNING-----")

    hot_avg_timestamp = hot_avg_timestamp.replace(tzinfo=pytz.utc)

    if hot_avg_timestamp < (now_in_utc() - hot_recalc_threshold):
        call_hot_average()

    count = 0

    def call_all_hot_window_scores():
        if hot_eligible_age:
            calc_all_hot_window_scores(hot_eligible_age)
        else:
            calc_all_hot_window_scores()

    def get_mass_time():
        mass_timestamp = None

        try:
            mass_timestamp = get_key_from_stat('mass_hot_window_timestamp', type = 'datetime')
        except sqlalchemy.orm.exc.NoResultFound:
            call_all_hot_window_scores()

        if type(mass_timestamp) == dict:
            return mass_timestamp['value']
        else:
            return None

    mass_timestamp = None

    while mass_timestamp == None and count < 5:
        mass_timestamp = get_mass_time()
        count += 1

    if count >= 5:
        print("\t-----WARNING WARNING WARNING-----\n\tSomething has gone tragically wrong with the hotness: MASS.\n\t-----WARNING WARNING WARNING-----")

    mass_timestamp = mass_timestamp.replace(tzinfo=pytz.utc)

    if mass_timestamp < (now_in_utc() - hot_recalc_threshold):
        call_all_hot_window_scores()

    return 0

def get_hot_stories(hot_eligible_age = timedelta(hours = 48)):
    """
    Get a story list that is suitable for display as "hot".
    @param timediff: timedelta object representing hot story eligibility age
    """
    hot_avg = get_key_from_stat('hot_avg')['value']
    stories = dbsession.query(Submission).options(joinedload('submitter')).filter(Submission.deleted == False).filter(Submission.added_on > (now_in_utc() - hot_eligible_age)).filter(Submission.hot_window_score > hot_avg).order_by(Submission.hot_window_score.desc())
    return stories

def get_controversial_stories(timediff = timedelta(hours = 48), contro_threshold = 5, contro_min = 10):
    """
    Get a story list that is suitable for display as "controversial".
    @param timediff: timedelta representing controversial eligibility age
    @param contro_threshold: the maximum difference between up and down votes to be considered "controversial"
    @param contro_min: the minimum number of points required for something to appear as controversial
    @return: SA query ready to get list of stuff
    """
    stories = dbsession.query(Submission).options(joinedload('submitter')).filter(Submission.deleted == False).filter(Submission.added_on > (now_in_utc() - timediff)).filter(func.abs(Submission.upvote_tally - Submission.downvote_tally) <= contro_threshold).filter(Submission.total_vote_tally > contro_min).order_by(Submission.added_on.desc())
    return stories

def count_story_votes(submission_id):
    dv_num = dbsession.query(Vote).filter(Vote.points < 0).filter(Vote.submission_id == submission_id).count()
    story = get_story_by_id(submission_id)
    story.downvote_tally = dv_num
    story.downvote_tally_timestamp = now_in_utc()

    uv_num = dbsession.query(Vote).filter(Vote.points > 0).filter(Vote.submission_id == submission_id).count()
    story.upvote_tally = uv_num
    story.upvote_tally_timestamp = now_in_utc()

    story.total_vote_tally = uv_num + dv_num
    story.total_vote_timestamp = now_in_utc()

    dbsession.add(story)
    dbsession.flush()

    return [dv_num, uv_num]

def recentize_contro(recalc_timediff = timedelta(seconds = 1), age_timediff = timedelta(hours = 48)):
    """
    Ensure that upvote and downvote tallies of stories added in the last age_timediff time
    are no older than recalc_timediff time. Recalculate if so, do nothing if not.
    """
    stories = dbsession.query(Submission).filter(Submission.deleted == False).filter(Submission.added_on > (now_in_utc() - age_timediff)).filter(sqlalchemy.or_(sqlalchemy.or_(Submission.upvote_tally_timestamp < (now_in_utc() - recalc_timediff), Submission.downvote_tally_timestamp < (now_in_utc() - recalc_timediff)), sqlalchemy.or_(Submission.upvote_tally_timestamp == None, Submission.downvote_tally_timestamp == None))).all()
    for s in stories:
        count_story_votes(s.id)

    return 0

def realize_timedelta_constructor(con_str):
    """ Converts a timedelta constructor parameter list into a real timedelta.
    @param con_str: the constructor parameters to convert"""
    return eval("timedelta({0})".format(con_str))

#stories
def get_story_list(page_num = 1, per_page = 30, sort = 'new', request = None):
    stories = dbsession.query(Submission).options(joinedload('submitter')).filter(Submission.deleted == False)

    if sort == 'top':
        stories = stories.order_by(Submission.points.desc())
    if sort == 'hot':
        if request and 'sort.hot_point_window' in request.registry.settings:
            sets = request.registry.settings
            recentize_hots(hot_point_window = realize_timedelta_constructor(sets['sort.hot_point_window']), hot_eligible_age = realize_timedelta_constructor(sets['sort.hot_eligible_age']), hot_recalc_threshold = realize_timedelta_constructor(sets['sort.hot_recalc_threshold']))
            stories = get_hot_stories(hot_eligible_age = realize_timedelta_constructor(sets['sort.hot_eligible_age'])) 
        else:
            recentize_hots()
            stories = get_hot_stories()
    if sort == 'new':
        stories = stories.order_by(Submission.added_on.desc())
    if sort == 'contro':
        recentize_contro()
        stories = get_controversial_stories()

    max_stories = count_sa_obj(stories)

    endpoints = get_endpoints_from_page_num(page_num, per_page)
    return {'stories': stories[endpoints['start']:endpoints['end']], 'max_stories': max_stories}

def get_story_by_id(id):
    return dbsession.query(Submission).options(joinedload('submitter')).filter(Submission.id == id).one()

#def get_all_stories_with_user_votes(user_id):
#    stories = get_all_stories()
#    vote_dict = {}
#    for s in stories:
#        vote_dict[s.id] = []
#        vs = dbsession.query(s.votes).filter(Vote.user_id == user_id).all()
#        [vote_dict[s.id].append(v.direction) for v in vs]
#    print(vote_dict)
#    return {'stories': stories, 'vote_dict': vote_dict}

def update_story_vote_tally(story_id):
    if type(story_id) is list:
        for sid in story_id:
            get_story_by_id(sid).tally_votes()
    #@TODO: implement the single str/UUID form here too
    #@TODO: implement caching

def get_endpoints_from_page_num(page_num, per_page):
    if type(page_num) != int:
        try:
            page_num = int(page_num)
        except:
            page_num = 0

    if type(per_page) != int:
        try:
            per_page = int(per_page)
        except:
            per_page = 30

    if page_num > 0:
        start = (page_num - 1) * per_page
        end = page_num * per_page
    else:
        start = 0
        end = per_page
    return {'start': start, 'end': end}

def get_comments_by_story_id(id, organize_parentage = False, page_num = 1, per_page = 30, sort = 'new'):
    if not organize_parentage:
        return dbsession.query(Comment).filter(Comment.submission_id == id).all()
    else:
        #@TODO: this will probably be slow in practice and would be better off as a hand-rolled SQL query
        # not implementing that at the moment because I want database agnosticism, but perhaps I will include
        # a statement for PostgreSQL soon. It could be used on Pg installs and as an example for others.
        tree = {}
        tree[id] = []
        dex = {}
        all_comments = dbsession.query(Comment).filter(Comment.submission_id == id).all()
        roots = dbsession.query(Comment).filter(Comment.submission_id == id).filter(Comment.submission_id == Comment.parent_id)
        max_roots = count_sa_obj(roots)

        if sort == 'new':
            roots = roots.order_by(Comment.added_on.desc())
        elif sort == 'sunshine':
            roots = x
        elif sort == 'ajaja':
            roots = x
            etc

        endpoints = get_endpoints_from_page_num(page_num, per_page)
        limited_roots = roots[endpoints['start']:endpoints['end']]

        allowed_roots = [ ]

        for root in limited_roots:
            allowed_roots.append(str(root.id))

        structures = _build_comment_structures(all_comments, allowed_roots, tree, {})
        tree = structures['tree']
        dex = structures['dex']
        return {'tree': tree, 'dex': dex, 'comments': all_comments, 'max_comments': max_roots, }

def _build_comment_structures(all_comments, allowed_roots, tree, dex):
    for c in all_comments:
        # make c.parent_id a string; this function receives UUIDs as strings
        # @todo: we really need to unfungle the str/UUID conversion thing,
        # it is inconsistent throughout the application

        c.parent_id = str(c.parent_id)
        if c.parent_id in allowed_roots or str(c.id) in allowed_roots:
            # skip childless deleted comments
            if c.body == '[deleted]':
                kid_count = count_comment_children(c.id)
                if kid_count <= 0:
                    continue
            if c.parent_id not in tree:
                tree[c.parent_id] = []
            if str(c.id) not in tree[c.parent_id]:
                tree[c.parent_id].append(str(c.id))
                dex[str(c.id)] = c
                # every comment written has potential children
                # we must, therefore, allow it as a root
                allowed_roots.append(str(c.id))
                #@FIXME: there is a strong possibility that this is excessive recursion
                # we should think about it and make this not re-loop over itself every time
                # a new comment is added an official comment. mostly no-ops but I have a
                # feeling that this is much more convoluted than necessary.
                # however, i have worked on this a good long time and must stop now.
                # it's working like this. one day, it should be reconsidered.
                structure = _build_comment_structures(all_comments, allowed_roots, tree, dex)
                tree = structure['tree']
                dex = structure['dex']
                allowed_roots = structure['allowed_roots']

    return {'tree': tree, 'dex': dex, 'allowed_roots': allowed_roots}

def count_comment_children(comment_id):
    """
    Counts *only* direct children of a given comment id.
    @param comment_id: the id whose children we should count
    @return: the number of immediate children
    """
    heritage = dbsession.query(Comment).filter(Comment.parent_id == comment_id).all()
    return len(heritage)

def count_sa_obj(obj):
    """
    Accept an SA query object and append .count() to tally the total applicable number.
    This is used to tell if we need pagination controls.
    @param obj: a Sqlalchemy query object
    @return: an integer representing the potential number of rows
    """
    return obj.count()

def get_comment_parent_story(id):
    try:
        return dbsession.query(Comment.submission_id).filter(Comment.id == id).one()
    except:
        return None

def get_comment_by_id(id):
    return dbsession.query(Comment).filter(Comment.id == id).one()

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

    from raggregate.models import UserPicture
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
    return dbsession.query(Epistle, Comment).filter(sqlalchemy.or_(user.id == Epistle.recipient, user.id == Comment.in_reply_to)).filter(sqlalchemy.or_(Epistle.unread == True, Comment.unread == True)).count()

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
    return dbsession.query(Comment).filter(sqlalchemy.and_(Comment.unread == True, Comment.in_reply_to == id)).all()

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
    return tostring(lx, method="text")

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
