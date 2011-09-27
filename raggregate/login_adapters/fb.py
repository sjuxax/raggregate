# this file is named fb.py to prevent conflicts with facebook's python-sdk
# which is also named "facebook"

import facebook
from raggregate.models import User
import sqlalchemy
from raggregate import queries
from raggregate.login_adapters import LoginAdapterExc

import sqlahelper
dbsession = sqlahelper.get_session()

def extract_from_cookie(request):
    r = request
    rrs = request.registry.settings

    fb_cookie = facebook.get_user_from_cookie(request.cookies, rrs['facebook.app_key'], rrs['facebook.app_secret'])
    
    if fb_cookie is None:
        raise LoginAdapterExc("No Facebook login.")

    graph = facebook.GraphAPI(fb_cookie['access_token'])
    try:
        u_fbinfo = graph.get_object("me")
    except facebook.GraphAPIError:
        # happens occasionally when the user has already logged out
        raise LoginAdapterExc("User is not logged into Facebook anymore")

    r.session['u_fbgraph'] = graph
    r.session['u_fbinfo'] = u_fbinfo

    return {'info': u_fbinfo, 'local_username': "fb-{id}".format(id=u_fbinfo['id']), 'request': r}

def create_local_user(fb_info, local_username, request = None): 
    u = queries.create_user(origination='facebook', remote_object=fb_info, username=local_username)
    if request:
        profile_picture = request.session['u_fbgraph'].get_connections(fb_info['id'], "picture")
        up = queries.add_user_picture("{0}-fbprofile.jpg".format(fb_info['id']), fb_info['id'], request.registry.settings['user.picture_upload_directory'], profile_picture)
        u.picture = up
        dbsession.add(u)
    return u
