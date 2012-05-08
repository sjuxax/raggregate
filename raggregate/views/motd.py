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
    #if 'logged_in_admin' not in session or session['logged_in_admin'] == False:
    #    return HTTPNotFound()

    # Ensure user is logged in
    if 'logged_in' not in session:
        session['message'] = 'Sorry, you must <a href="{0}">log in</a> before you can add a message of the day.'.format(request.route_url('login'))
        return {'messages_of_the_day': [], 'success': False, 'code': 'ENOLOGIN'}

    # Handle the form input
    if post and post['message_to_add'] != '':
        message_to_add = post['message_to_add']
        author = post['author']

        #@TODO: Need to add more form validation here
        if author == "":
            author = "Unknown"

        try:
            new_MOTD = MOTD(message_to_add, author, session['users.id'])
            dbsession.add(new_MOTD)
            dbsession.commit()
            session['message'] = "Message of the Day Added!"
        except Exception, ex:
            print str(ex)

    messages_of_the_day = motd_queries.get_all_messages()
    return {'messages_of_the_day': messages_of_the_day}
