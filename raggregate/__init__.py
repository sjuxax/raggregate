from pyramid.config import Configurator
from sqlalchemy import engine_from_config

import pyramid_beaker
import sqlahelper

from raggregate.models import initialize_sql

from pyramid.events import BeforeRender
from pyramid.events import NewRequest
from pyramid.events import NewResponse
from raggregate import subscribers

from pyramid.request import Request

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.scan('raggregate.models')
    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)
    initialize_sql(engine)

    session_factory = pyramid_beaker.session_factory_from_settings(settings)

    template_static_asset = "{0}/static".format(settings['mako.directories'])
    settings['template_static_asset'] = template_static_asset

    config = Configurator(settings=settings)
    config.include('pyramid_tm')

    if 'solr.address' in settings:
        import sunburnt
        solr_conn = sunburnt.SolrInterface(settings['solr.address'])
        config.registry.solr_conn = solr_conn

    if 'twitter.app_key' in settings and 'twitter.app_secret' in settings:
        from twython import Twython
        app_twit = Twython(twitter_token = settings['twitter.app_key'],
                           twitter_secret = settings['twitter.app_secret'])
        config.registry.app_twit = app_twit

    config.set_session_factory(session_factory)

    # @TODO: the name "mako.directories" implies this could be a list
    # right now we don't care. Someone should fix this.
    config.add_static_view('static', template_static_asset)
    config.add_static_view('user_imgs', settings['user.picture_upload_package'])

    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('post', '/post')
    config.add_route('ban', '/ban')
    config.add_route('vote', '/vote/{way}')
    config.add_route('full', '/full/{sub_id}')
    config.add_route('epistle', '/messages/{box}')
    config.add_route('follow', '/follow')
    config.add_route('save', '/save')
    config.add_route('search', '/search')
    config.add_route('twit_sign', '/twit_sign')
    config.add_route('user_info', '/user_info')
    config.add_route('buttons', '/buttons')
    config.add_route('favicon', '/favicon.ico')
    config.add_route('atom_story', '/atom_story.xml')
    config.add_route('atom_self_story', '/atom_self_story.xml')
    config.add_route('atom_combined', '/atom_combined.xml')
    config.add_route('atom_comment', '/atom_comment.xml')
    config.add_route('section', '/section')

    config.add_subscriber(subscribers.ban, NewResponse)
    config.add_subscriber(subscribers.user_session_handler, BeforeRender)
    config.add_subscriber(subscribers.clear_per_request_session, NewRequest)
    config.add_subscriber(subscribers.clean_inputs, NewRequest)

    config.scan('raggregate.views')


    pyramid_beaker.set_cache_regions_from_settings(settings)

    return config.make_wsgi_app()

