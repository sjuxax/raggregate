import sqlalchemy

from raggregate.models import DBSession
from raggregate.models import Vote
from raggregate.models import Submission
from raggregate.models import Comment
from raggregate.models import Epistle

from raggregate import queries

from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound

import re

@view_config(renderer='post.mak', route_name='post')
@view_config(renderer='post.mak', route_name='home')
def post(request):
    s = request.session
    p = request.session['safe_post']
    r = request
    qs = s['safe_get']
    s['message'] = "Post a story."
    dbsession = DBSession()
    stories = None
    if 'new_post' in qs and qs['new_post'] == 'y':
        if 'logged_in' not in s:
            s['message'] = 'Sorry, please log in first'
            return {'stories': [], 'success': False, 'code': 'ENOLOGIN'}

    if p and 'title' in p:
        if 'logged_in' not in s:
            s['message'] = 'Sorry, please log in first'
            return {'stories': [], 'success': False, 'code': 'ENOLOGIN'}
        if p['url'] != '' and p['url'] is not None:
            p['url'] = queries.strip_all_html(p['url'])
            if not re.match(r'http[s]*:\/\/', p['url']):
                p['url'] = 'http://' + p['url']
        else:
            # set to None so that NULL goes into the database
            p['url'] = None


        sub = Submission(p['title'], p['description'], p['url'], s['users.id'])
        dbsession.add(sub)
        s['message'] = "Added."

        try:
            if request.registry.solr_conn:
                # we flush here to ensure we have a vaild id object when added to solr
                # we use this if statement so that the exception will be raised before
                # dbsession is flushed, hence avoiding an unnecessary flush if the site
                # is not using solr.
                dbsession.flush()
                request.registry.solr_conn.add({'id': sub.id, 'title': sub.title, 'description': sub.description})
                request.registry.solr_conn.commit()
        except AttributeError:
            #solr is not configured for this connection
            pass

    if r.params and 'op' in r.params:
        sub_id = r.params['sub_id']
        if r.params['op'] == 'del':
            try:
                story_to_del = queries.get_story_by_id(sub_id)
            except sqlalchemy.orm.exc.NoResultFound:
                story_to_del = None
            if story_to_del:
                if queries.is_user_allowed_admin_action(s['users.id'], str(story_to_del.id), ):
                        # don't delete for real anymore
                        # just zero out content
                        # this is important so that comments, etc., don't die
                        # dbsession.delete(story_to_del)
                        story_to_del.description = "[deleted]"
                        story_to_del.url = "#"
                        story_to_del.title = "[deleted]"
                        story_to_del.deleted = True
                        dbsession.add(story_to_del)
                        dbsession.flush()
                else:
                    print("Illegal deletion attempted on {0}".format(story_to_del.submitter.id))

    sort = 'new'
    page_num = 1
    per_page = 30
    next_page = None
    prev_page = None

    # only pass through approved sort options
    if 'sort' in qs:
        if qs['sort'] == 'top':
            sort = 'top'
        if qs['sort'] == 'hot':
            sort = 'hot'
        if qs['sort'] == 'contro':
            sort = 'contro'

    if 'page_num' in qs:
        try:
            page_num = int(qs['page_num'])
        except:
            page_num = 1

#   @FIXME: make per_page configurable in a safe location
#   it is probably unwise to allow this to be set in the query string
#   because then a malicious user could say per_page = 10000000000
#   and easily launch a DoS via that mechanism.
#   if 'per_page' in qs:
#       per_page = qs['per_page']

    stories = queries.get_story_list(page_num = page_num, per_page = per_page, sort = sort)
    max_stories = stories['max_stories']
    stories = stories['stories']

    # this should be split into its own def under queries.py
    # as it is currently used in at least one other place
    if max_stories > (page_num * per_page):
        next_page = page_num + 1

    if page_num > 1:
        prev_page = page_num - 1

    vote_dict = {}
    if 'logged_in' in s:
        vote_dict = queries.get_user_votes_on_all_submissions(s['users.id'])
    for s in stories:
        #@TODO: Remember to not tally on every load once a real site deploys
        s.tally_votes()
        s.tally_comments()

    return {'stories': stories, 'success': True, 'code': 0, 'vote_dict': vote_dict, 'max_stories': max_stories,
            'prev_page': prev_page, 'next_page': next_page, }

@view_config(renderer='vote.mak', route_name='vote')
def vote(request):
    s = request.session
    p = request.session['safe_post']
    dbsession = DBSession()
    if 'logged_in' in s:
        way = request.matchdict['way']
        if way == 'up':
            points = 1
        elif way == 'down':
            points = -1

        comment_id = None
        if 'target_type' in p and p['target_type'] == 'comment':
            # the post comes in with comment id in sub_id spot
            # here, we make sub_id the real sub_id
            sub_id = queries.get_comment_parent_story(p['sub_id'])[0]
            comment_id = p['sub_id']
            vote_list = dbsession.query(Vote).filter(Vote.comment_id == comment_id).filter(Vote.user_id == s['users.id']).all()
        else:
            sub_id = p['sub_id']
            vote_list = dbsession.query(Vote).filter(Vote.submission_id == p['sub_id']).filter(Vote.comment_id == None).filter(Vote.user_id == s['users.id']).all()

        # find out if the user has already voted on this submission
        if len(vote_list) > 0:
            if vote_list[0].direction == points:
                return {'message': 'You have already voted on this submission.', 'code': 'EOLDVOTE', 'success': False}
            else:
                dbsession.delete(vote_list[0])

        v = Vote(sub_id, s['users.id'], points, p['target_type'], comment_id)
        v.direction = points
        dbsession = DBSession()
        dbsession.add(v)
        return HTTPFound(p['jump_to'])
    else:
        return {'message': 'Sorry, you are not logged in.', 'code': 'ENOLOGIN', 'success': False}

@view_config(renderer='full.mak', route_name='full')
def full(request):
    message = ''
    #@TODO: Change this to use slugs instead of literal guids
    sub_id = request.matchdict['sub_id']
    dbsession = DBSession()
    p = request.session['safe_post']
    prm = request.session['safe_params']
    s = request.session
    logged_in = False

    if 'logged_in' in s:
        #return {'message': 'Sorry, please log in first.', 'story': {}, 'comments': {}, 'success': False, 'code': 'ENOLOGIN'}
        logged_in = True

    # record the comment
    if 'op' in prm and prm['op'] == 'del' and logged_in:
        if 'comment_id' in prm:
            c = queries.get_comment_by_id(prm['comment_id'])
            if queries.is_user_allowed_admin_action(s['users.id'], str(c.id), ):
                c.body = "[deleted]"
                dbsession.add(c)
        s['message'] = 'Comment deleted.'
    if 'op' in prm and prm['op'] == 'edit' and logged_in:
        if 'comment_id' in prm:
            c = queries.get_comment_by_id(prm['comment_id'])
            if queries.is_user_allowed_admin_action(s['users.id'], str(c.id), ):
                c.body = prm['body']
                dbsession.add(c)
        s['message'] = 'Comment updated.'
    else:
        if 'description-textarea' in request.session['safe_post'] and logged_in:
            sub = queries.get_story_by_id(sub_id)
            if queries.is_user_allowed_admin_action(s['users.id'], str(sub.id)):
                sub.description = prm['description-textarea']
                dbsession.add(sub)
            s['message'] = 'Description updated.'
        if 'body' in request.session['safe_post'] and logged_in:
            c = Comment(sub_id, s['users.id'], p['comment_parent'], prm['body'])
            # send a message to a comment's immediate parent
            e = Epistle(queries.find_by_id(p['comment_parent']).submitter.id, s['users.id'], p['body'], parent_type = p['parent_type'], parent = p['comment_parent'])
            dbsession.add(e)
            dbsession.add(c)
            s['message'] = 'Comment added.'
    #@TODO: Stop using SA queries in views, move them to individual models
    story = queries.get_story_by_id(sub_id)
    story.tally_votes()
    story_vote_dict = {}
    comment_vote_dict = {}

    if logged_in:
        # see queries.py; these two should not be separate. #@FIXME
        story_vote_dict = queries.get_user_votes_on_submission(s['users.id'], sub_id)
        comment_vote_dict = queries.get_user_votes_on_submissions_comments(s['users.id'], sub_id)

    page_num = 1
    per_page = 30
    sort = 'new'
    next_page = None
    prev_page = None

    if 'page_num' in prm:
        try:
            page_num = int(prm['page_num'])
        except:
            page_num = 1

    # comments returns a dict; see queries.py
    comments = queries.get_comments_by_story_id(sub_id, organize_parentage=True, page_num = page_num, per_page = per_page, sort = sort)

    for c in comments['comments']:
        #@TODO: Don't do this on every load on a real deployment
        c.tally_votes()

    if page_num > 1:
        prev_page = page_num - 1

    if comments['max_comments'] > (page_num * per_page):
        next_page = page_num + 1

    return {'story': story, 'comments': comments, 'success': True, 'code': 0, 'story_vote_dict': story_vote_dict,
            'comment_vote_dict': comment_vote_dict, 'next_page': next_page, 'prev_page': prev_page, }
