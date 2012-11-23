from raggregate.models.submission import Submission
from raggregate.models.comment import Comment
from raggregate.models.vote import Vote
from raggregate.models.subscribe import Subscribe
from raggregate.models.section import Section

from raggregate.queries import hotness
from raggregate.queries import subscribe as sub_queries
from raggregate.queries import section as section_queries
from raggregate.queries import general

import sqlahelper
from sqlalchemy.orm import joinedload

dbsession = sqlahelper.get_session()

#stories
def get_story_list(page_num = 1, per_page = 30, sort = 'new', request = None, self_only = False, section = None):
    if 'users.id' in request.session and request.session['users.id'] is not None:
        user_id = request.session['users.id']
    else:
        user_id = None

    stories = dbsession.query(Submission).options(joinedload('submitter')).filter(Submission.deleted == False)

    if section and section.__class__ == Section:
        stories = stories.filter(Submission.section == section.id)
    elif section and section == 'all':
        pass
    else:
        # show default user sections
        if user_id is not None:
            # Get a list of sections that this user is subscribed to
            subscribed_to_list = sub_queries.get_subscribed_by_user_id(user_id)
            # Filter sections by the list we just retreived
            if len(subscribed_to_list) > 0:
                stories = stories.filter(Submission.section.in_(subscribed_to_list))

    if self_only:
        stories = stories.filter(Submission.self_post == True)

    if sort == 'top':
        stories = stories.order_by(Submission.points.desc())
    if sort == 'hot':
        if request and 'sort.hot_point_window' in request.registry.settings:
            sets = request.registry.settings
            hotness.recentize_hots(hot_point_window = general.realize_timedelta_constructor(sets['sort.hot_point_window']),
                                   hot_eligible_age = general.realize_timedelta_constructor(sets['sort.hot_eligible_age']),
                                   hot_recalc_threshold = general.realize_timedelta_constructor(sets['sort.hot_recalc_threshold']))
            stories = hotness.get_hot_stories(hot_eligible_age = general.realize_timedelta_constructor(sets['sort.hot_eligible_age'])) 
        else:
            hotness.recentize_hots()
            stories = hotness.get_hot_stories()
    if sort == 'new':
        stories = stories.order_by(Submission.added_on.desc())
    if sort == 'contro':
        hotness.recentize_contro()
        stories = hotness.get_controversial_stories()

    max_stories = general.count_sa_obj(stories)

    endpoints = get_endpoints_from_page_num(page_num, per_page)
    return {'stories': stories[endpoints['start']:endpoints['end']], 'max_stories': max_stories}

def get_story_by_id(id):
    return dbsession.query(Submission).options(joinedload('submitter')).filter(Submission.id == id).one()

def get_story_by_url_oldest(url):
    """
    Return the oldest instance of a post that matches the passed URL if there is such a post.
    @param url: url to match
    @return: matching raggregate.models.Submission object if found, otherwise False
    """
    q = dbsession.query(Submission).filter(Submission.url == url).order_by(Submission.added_on.asc()).limit(1)
    res = q.all()
    if len(res) > 0:
        return res[0]
    else:
        return False


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

def get_comments(id, organize_parentage = False, page_num = 1, per_page = 30, sort = 'new', target = 'story', target_id = None):
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
        if target == 'story':
            roots = dbsession.query(Comment).filter(Comment.submission_id == id).filter(Comment.submission_id == Comment.parent_id)
        elif target == 'comment':
            roots = dbsession.query(Comment).filter(Comment.submission_id == id).filter(target_id == Comment.id)

        max_roots = general.count_sa_obj(roots)

        if sort == 'top':
            roots = roots.order_by(Comment.points.desc())
        else:
            # use "new" as default sort option
            roots = roots.order_by(Comment.added_on.desc())

        endpoints = get_endpoints_from_page_num(page_num, per_page)
        allowed_roots = [ ]
        [allowed_roots.append(str(root.id)) for root in roots[endpoints['start']:endpoints['end']]]

        trees = _build_comment_trees(all_comments, allowed_roots)
        tree = trees['tree']
        dex = trees['dex']
        allowed_roots = trees['allowed_roots']
        return {'tree': tree, 'dex': dex, 'comments': all_comments, 'max_comments': max_roots, 'allowed_roots': allowed_roots}

def _build_comment_trees(all_comments, allowed_roots):
    tree = {}
    dex = {}

    for c in all_comments:
        # make c.parent_id a string; this function receives UUIDs as strings
        # @todo: we really need to unfungle the str/UUID conversion thing,
        # it is inconsistent throughout the application
        c.parent_id = str(c.parent_id)
        # add comment to index for template lookup
        dex[str(c.id)] = c
       # do not compile deleted comments with no children, and remove them from allowed_roots if they exist
        if c.deleted:
            if count_comment_children(c.id) < 1:
                if str(c.id) in allowed_roots:
                    allowed_roots.remove(str(c.id))
                continue
        # do not compile roots in this tree; use allowed_roots
        if str(c.submission_id) == c.parent_id:
            continue
         # add parent id to tree if it doesn't exist
        if c.parent_id not in tree:
            tree[c.parent_id] = []
        # add this comment as a child of its parent
        tree[c.parent_id].append(str(c.id))

    return {'tree': tree, 'dex': dex, 'allowed_roots': allowed_roots}

def count_comment_children(comment_id):
    """
    Counts *only* direct children of a given comment id.
    @param comment_id: the id whose children we should count
    @return: the number of immediate children
    """
    heritage = dbsession.query(Comment).filter(Comment.parent_id == comment_id).filter(Comment.deleted == False).all()
    return len(heritage)

def get_comment_parent_story(id):
    try:
        return dbsession.query(Comment.submission_id).filter(Comment.id == id).one()
    except:
        return None

def get_comment_by_id(id):
    return dbsession.query(Comment).filter(Comment.id == id).one()

def get_recent_comments(num):
    """
    Get the last num comments.
    @param num: number of comments to list
    @return: list with num most recent comments as sa objects.
    """
    return dbsession.query(Comment).filter(Comment.deleted == False).order_by(Comment.added_on.desc()).limit(num).all()

def get_story_id_from_slug(slug):
    try_slug = True
    # if our "slug" is the same length as a uuid
    # try the uuid first, since it's more likely
    # a uuid and NOT a slug.
    #
    # this breaks badly if it actually runs on a slug.
    # because pgsql throws an error, we must explicitly
    # roll back the current transaction, or everything
    # else will also die.
    if len(unicode(slug)) == 36:
        try:
            s = get_story_by_id(slug)
            try_slug = False
        except:
            from pyramid_tm import transaction
            transaction.abort()
            transaction.begin()

    if try_slug:
        try:
            s = dbsession.query(Submission).filter(Submission.slug == slug).one()
        except:
            s = get_story_by_id(slug)

    return str(s.id)
