import sqlalchemy

from raggregate import queries

from pyramid.response import Response
from pyramid.view import view_config

from raggregate.models import DBSession
from raggregate.models import Epistle

@view_config(renderer='epistle.mak', route_name='epistle')
def epistle(request):
    message = ''
    dbsession = DBSession()
    s = request.session
    p = request.session['safe_post']

    if 'logged_in' not in s:
        s['message'] = 'Sorry, you must be logged in to use the messaging feature.'
        return {'success': False, 'code': 'ENOLOGIN'}

    if p and 'recipient' in p:
        if p['recipient'] == '' and p['recipient-name'] == '':
            s['message'] = "No recipient provided."
            return {'code': 'ENORECP', 'success': False}
        if p['recipient'] == '':
            # look up recipient-name
            try:
                recp = queries.get_user_by_name(p['recipient-name'])
            except sqlalchemy.orm.exc.NoResultFound:
                #@TODO: discuss facebook name sending implications
                s['message'] = "Could not find that user."
                return {'code': 'ENORECP', 'success': False}
        else:
            try:
                recp = queries.get_user_by_id(p['recipient'])
            except:
                s['message'] = "Could not find that user."
                return {'code': 'ENORECP', 'success': False}

        if p['subject'] == '':
            subject = None
        else:
            subject = p['subject']

        if 'parent_id' not in p or p['parent_id'] == '':
            parent_id = None
            parent_type = 'epistle'
        else:
            parent_id = p['parent_id']
            parent_type = 'reply'

        body = p['body']
        ep = Epistle(recp.id, s['users.id'], body, parent=parent_id, parent_type=parent_type, subject=subject)
        dbsession.add(ep)
        message = 'Message sent.'

    box = request.matchdict['box']

    ep = queries.get_epistle_roots(id=s['users.id'], target=box)
    epistle_children = {}

    for e in ep:
        e_id = str(e.id)
        epistle_children[e_id] = queries.get_epistle_children(e.id)

    flat_eps = []
    [flat_eps.append(e) for e in _unwrap_list(ep)]
    [flat_eps.append(e) for e in _unwrap_list(epistle_children.values())]

    for e in flat_eps:
        queries.mark_epistle_read(e)
        e = _assign_epistle_parent(e)

    return {'epistles': {'roots': ep, 'children': epistle_children}, 'success': True, 'code': 0,}

def _unwrap_list(lst):
    for l in lst:
        if type(l) != list:
            yield l
        else:
            for i in _unwrap_list(l):
                yield i

def _assign_epistle_parent(e):
    #@TODO: REALLY need to put parent_info somewhere smarter, and/or not make this happen so much
    if e.parent:
        if e.parent_type == 'story':
            e.parent_info = queries.get_story_by_id(e.parent)
        elif e.parent_type == 'comment':
            e.parent_info = queries.get_comment_by_id(e.parent)
        elif e.parent_type == 'epistle' or e.parent_type == 'reply':
            e.parent_info = queries.get_epistle_by_id(e.parent)
    return e
