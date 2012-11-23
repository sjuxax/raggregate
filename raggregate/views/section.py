from raggregate.queries import section as section_queries

from pyramid.view import view_config

from raggregate.models import DBSession
from raggregate.models.section import Section

from pyramid.httpexceptions import HTTPNotFound

@view_config(renderer='section.mak', route_name='section')
def story(request):
    s = request.session
    r = request
    p = s['safe_post']
    dbsession = DBSession()

    #@TODO: unify admin-only page handling so that we can easily change this
    # some day if we want.
    if 'logged_in_admin' not in s or s['logged_in_admin'] == False:
        return HTTPNotFound()

    if 'name' in p and p['name'] != '':
        name = p['name'].strip()
        new_sect = Section(name = name, added_by = s['users.id'])
        dbsession.add(new_sect)
        s['message'] = "Section {0} successfully added.".format(p['name'])

    sections = section_queries.get_sections()
    return {'sections': sections}
