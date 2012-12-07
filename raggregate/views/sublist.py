from raggregate.queries import sublist as sublist_queries

from pyramid.view import view_config

from raggregate.models import DBSession
from raggregate.models.sublist import Sublist
from raggregate.models.sublist_member import SublistMember

from pyramid.httpexceptions import HTTPNotFound

@view_config(renderer='sublist.mak', route_name='sublistc')
def sublist_create(request):
    s = request.session
    r = request
    p = s['safe_post']
    dbsession = DBSession()

    if 'title' in p and p['title'] != '':
        title = p['title'].strip()
        description = p['description']
        visibility = p['visibility']
        new_list = Sublist(title = title, description = description,
                           visibility = visibility, added_by = s['users.id'])
        dbsession.add(new_list)
        s['message'] = "Sublist {0} successfully added.".format(p['title'])

    sublists = sublist_queries.get_sublists()
    return {'sublists': sublists, 'stories': []}

@view_config(renderer='sublist.mak', route_name='sublist')
def sublist_read(request):
    s = request.session
    r = request
    p = s['safe_post']
    sub_title = request.matchdict['sub_title']
    dbsession = DBSession()

    sublist = sublist_queries.get_sublist_by_title(sub_title)[0]

    if 'new_members' in p and p['new_members'] != '':
        print "POST RECEIVED"
        for l in p['new_members'].splitlines():
            sm = SublistMember(sublist_id = sublist.id, member_id = l,
                           added_by = s['users.id'])
            dbsession.add(sm)

    stories = []
    #for l in sublist:
    l = sublist
    [stories.append(x) for x in sublist_queries.get_sublist_members(l.id)]
    return {'sublist': sublist, 'stories': stories, 'vote_dict': {}}
