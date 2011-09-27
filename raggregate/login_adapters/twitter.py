import sqlalchemy

from raggregate.models import User
from raggregate import queries

from twython import Twython

import sqlahelper

dbsession = sqlahelper.get_session()

def start_auth(request):
    app_twit = request.registry.app_twit
    auth_toks = app_twit.get_authentication_tokens()
    return auth_toks

def complete_auth(request, auth_toks):
    # create a twython object with our request-specific tokens
    # these tokens are used only to learn if the user accepted our request
    # for permissions.
    tmp_twit = Twython(twitter_token = request.registry.settings['twitter.app_key'],
                       twitter_secret = request.registry.settings['twitter.app_secret'],
                       oauth_token = auth_toks['oauth_token'],
                       oauth_token_secret = auth_toks['oauth_token_secret'])

    final_toks = tmp_twit.get_authorized_tokens()

    # create a session-permanent twython object containing the permanent tokens for this user.
    # this object must be used to read any data from the user's account.
    u_twit = Twython(twitter_token = request.registry.settings['twitter.app_key'],
                       twitter_secret = request.registry.settings['twitter.app_secret'],
                       oauth_token = final_toks['oauth_token'],
                       oauth_token_secret = final_toks['oauth_token_secret'])

    request.session['u_twit'] = u_twit

    username = "twit-{0}".format(final_toks['oauth_token'])
    screen_name = final_toks['screen_name']

    # check if user already exists; if not, please create
    try:
        u = queries.get_user_by_name(username)
        #@TODO: add something to ensure we are in sync with the twitter profile picture
        # unless specifically overridden by the user
    except sqlalchemy.orm.exc.NoResultFound:
        u = queries.create_user(origination='twitter', username=username, remote_object=final_toks)
        import urllib2
        image_data = urllib2.urlopen("http://api.twitter.com/1/users/profile_image/{0}.json".format(screen_name))
        orig_filename = "{0}-twitter-pic.png".format(screen_name)
        up_dir = request.registry.settings['user.picture_upload_directory']

        u.picture = queries.add_user_picture(orig_filename, str(u.id)[:7], up_dir, image_data)

        dbsession.add(u)

    return {'final_toks': final_toks, 'u': u} 
