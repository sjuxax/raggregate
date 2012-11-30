from raggregate.models import DBSession
from raggregate.models.motd import MOTD
from raggregate.queries import motd as motd_queries
from raggregate.queries import general
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
    if post:

        if 'add_motd_button' in post:

            message_to_add = general.get_from_post(post, 'message_to_add')
            author = general.get_from_post(post, 'author')
            source = general.get_from_post(post, 'source')
            link = general.get_from_post(post, 'link')
            datestring = general.get_from_post(post, 'datestring')
            added_by = session['users.id']

            if message_to_add:
                if not author:
                    author = 'Unknown'
                if not source:
                    source = 'No source'

                try:
                    new_motd = motd_queries.create_motd(message = message_to_add,
                            author = author, source = source, link = link,
                            added_by = added_by, datestring = datestring)
                    session['message'] = "Message of the Day Added!"
                except Exception, ex:
                    print str(ex)
                    session['message'] = 'There was a problem adding your message.'
                    return {'motds': [], 'success': False, 'code': 'EBADPOST'}
            else:
                session['message'] = 'Please enter a message'

    motds = motd_queries.get_all_messages()
    return {'motds': motds}
