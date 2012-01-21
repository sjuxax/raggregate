from raggregate import queries

from pyramid.view import view_config

from raggregate.models import DBSession


@view_config(renderer='atom_story.mak', route_name='atom_story')
def story(request):
    s = request.session
    r = request
    dbsession = DBSession()

    stories = queries.get_story_list(page_num = 1, per_page = 30, sort = 'new', request = r)
    last_update = stories['stories'][0].added_on.isoformat()
    request.response.content_type = "text/xml"
    site_name = r.registry.settings['site.site_name']
    return {'stories': stories['stories'], 'route': 'atom_story', 'last_update': last_update,
            'feed_title': '{0} stories'.format(site_name), 'feed_subtitle': 'newest stories on {0}'.format(site_name),
            'site_name': site_name,
           }


@view_config(renderer='atom_comment.mak', route_name='atom_comment')
def comment(request):
    s = request.session
    r = request
    dbsession = DBSession()

    comments = queries.get_recent_comments(20)
    last_update = comments[0].added_on.isoformat()
    request.response.content_type = "text/xml"
    site_name = r.registry.settings['site.site_name']
    return {'comments': comments, 'route': 'atom_comment', 'last_update': last_update,
            'feed_title': '{0} comments'.format(site_name), 'feed_subtitle': 'newest comments on {0}'.format(site_name),
            'site_name': site_name,
           }
