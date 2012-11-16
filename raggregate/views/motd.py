from raggregate.models import DBSession
from raggregate.models.motd import MOTD
from raggregate.new_queries import motd as motd_queries

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

@view_config(renderer='motd.mak', route_name='motd')
def motd(request):
    session = request.session
    post = session['safe_post']
    dbsession = DBSession()

    # Only allow admins to add a message at this time
    #@TODO: unify admin-only page handling so that we can easily change this
    # some day if we want.
    if 'logged_in_admin' not in session or session['logged_in_admin'] == False:
        return HTTPNotFound()

    # Handle the form input
    if post and post['new_motd'] != '':
        new_motd = post['new_motd']
        author = post['author']
        source = post['source']
        link = post['link']

        #@TODO: Need to add more form validation here
        if author == "":
            author = None

        try:
            new_motd = MOTD(message = new_motd, author = author,
                            source = source, link = link,
                            added_by = session['users.id'])
            dbsession.add(new_motd)
            session['message'] = "Message of the Day Added!"
        except Exception, ex:
            print str(ex)
            session['message'] = 'There was a problem adding your message.'
            return {'motds': [], 'success': False, 'code': 'EBADPOST'}

    motds = motd_queries.get_all_messages()
    return {'motds': motds}
