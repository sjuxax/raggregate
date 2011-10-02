from raggregate import queries
from raggregate.models import User

import sqlahelper

import datetime
import uuid
import os

import queries

from pyramid.url import static_url

from raggregate import template_filters

dbsession = sqlahelper.get_session()

def clean_inputs(event):
    request = event.request
    safe_post = {}
    safe_params = {}
    safe_get = {}

    if request.POST:
        p = request.POST
        for i in p.items():
            if i[0] != 'body' and i[0] != 'description':
                safe_i = queries.strip_all_html(i[1])
                safe_post[i[0]] = safe_i
            else:
                safe_post[i[0]] = i[1]
    if request.GET:
        get = request.GET
        for i in get.items():
            safe_i = queries.strip_all_html(i[1])
            safe_get[i[0]] = safe_i

    request.session['safe_get'] = safe_get
    request.session['safe_post'] = safe_post
    request.session['safe_params'] = dict(safe_get.items() + safe_post.items())

    return 0

def clear_per_request_session(event):
    # delete transient data stored in the session
    # this ensures a clean slate for the next request.
    s = event.request.session
    if 'message' in s:
        del s['message']
    if 'users.id' not in s:
        s['users.id'] = None

    return 0

def user_session_handler(event):
    s = event['request'].session
    r = event['request']
    e = event
    if 'message' in s:
        e['message'] = s['message']
    else:
        e['message'] = None

    e['template_filters'] = template_filters

    # this could be accessed by the request object, request.static_url()
    # should fixup the first here at least to be normal
    e['static_base'] = static_url("{0}/".format(r.registry.settings['template_static_asset']), r)
    e['static_url'] = static_url

    e['site_name'] = r.registry.settings['site.site_name']

    # export date fuzzing function to templates
    e['fuzzify_date'] = queries.fuzzify_date

    e['new_message_num'] = None
    e['karma'] = None
    e['u'] = None
    e['logged_in_admin'] = None
    e['logged_in'] = False

    e['followed_users'] = []

    if 'sort' in r.params:
        e['sort'] = r.params['sort']
    else:
        e['sort'] = 'new'

    if 'logged_in' in s:
        #@TODO: implement caching/rate limiting so we don't perform this on every single request anymore
        num = queries.get_new_message_num(s['users.id'])
        if num == 0:
            s['new_message_num'] = None
            e['new_message_num'] = None
        else:
            s['new_message_num'] = num
            e['new_message_num'] = num
        #@TODO: another calculation that would benefit from caching
        #if 'karma' in s:
        #    e['karma'] = s['karma']
        #    print 'AAAAAAAAAA' + str(s['karma'])
        #else:
        #not caching right now, commenting conditional
        karma = queries.get_user_by_id(s['users.id']).update_karma()
        s['karma'] = karma
        e['karma'] = karma

        if 'followed_users' in s and len(s['followed_users']) > 0:
            e['followed_users'] = s['followed_users']
        else:
            s['followed_users'] = queries.get_followed_users(s['users.id'])
            e['followed_users'] = s['followed_users']

        u = queries.get_user_by_id(s['users.id'])
        e['logged_in_admin'] = u.is_user_admin()
        e['u'] = u
        e['logged_in'] = True
    elif 'logged_in' not in s and r.registry.settings['user.generate_anon_accounts'] == 'true':
        # do not create a new user if we are on the login page
        # this simplifies anon -> permanent transfer
        if r.url.find('login') != -1:
            return
        # create a temporary user if this is a new session
        # all activity will be associated with this user until conversion to real account is performed
        u = User("{0}".format(uuid.UUID(bytes=os.urandom(16))), str(os.urandom(8)), real_name = "Unregistered User", temporary = True)
        dbsession.add(u)
        dbsession.flush()
        s['users.id'] = str(u.id)
        s['users.display_name'] = u.display_name()
        s['logged_in'] = True
        e['logged_in'] = True
