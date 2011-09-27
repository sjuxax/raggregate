import sqlalchemy

from raggregate import queries

from pyramid.response import Response
from pyramid.view import view_config

from raggregate.models import DBSession

@view_config(renderer='epistle.mak', route_name='epistle')
def epistle(request):
    message = ''
    dbsession = DBSession()
    s = request.session
    p = request.session['safe_post']

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
        else:
            parent_id = p['parent_id']

        body = p['body']
        ep = Epistle(recp.id, s['users.id'], body, parent=parent_id, parent_type='epistle', subject=subject)
        dbsession.add(ep)
        message = 'Message sent.'

    box = request.matchdict['box']
    #epistles = queries.get_epistle_by_recipient_id(s['users.id'])
    epistle_children = {}
    epistle_roots = {}
    if box == 'out':
        ep = queries.get_epistle_roots_by_recipient_id(s['users.id'])
    else:
        ep = queries.get_epistle_roots_by_sender_id(s['users.id'])

    for e in ep:
        e_id = str(e.id)
        epistle_roots[e_id] = e
        epistle_children[e_id] = queries.get_epistle_children(e.id)

    ep = queries.get_epistle_by_recipient_id(s['users.id'])
    for e in ep:
        if str(e.id) not in epistle_roots:
            epistle_roots[str(e.id)] = e

    flat_eps = []
    [flat_eps.append(e) for e in _unwrap_list(epistle_roots.values())]
    [flat_eps.append(e) for e in _unwrap_list(epistle_children.values()) if len(e) > 0]

    for e in flat_eps:
        queries.mark_epistle_read(e)
        e = _assign_epistle_parent(e)

    return {'epistles': {'roots': epistle_roots, 'children': epistle_children}, 'success': True, 'code': 0,}

def _unwrap_list(lst):
    for l in lst:
        if type(l) != list:
            yield l
        else:
            _unwrap_list(l)

def _assign_epistle_parent(e):
    if e.parent:
        if e.parent_type == 'story':
            e.parent_info = queries.get_story_by_id(e.parent)
        elif e.parent_type == 'comment':
            e.parent_info = queries.get_comment_by_id(e.parent)
        elif e.parent_type == 'epistle':
            e.parent_info = queries.get_epistle_by_id(e.parent)
    return e
