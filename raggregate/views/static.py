from pyramid.view import view_config
from pyramid.response import Response
from pyramid.path import AssetResolver

import os

@view_config(route_name='favicon')
def favicon_view(request):
    template_static_asset = request.registry.settings['template_static_asset']
    a = AssetResolver()
    icon = open(a.resolve("{0}/favicon.ico".format(template_static_asset)).abspath())
    return Response(content_type='image/x-icon', app_iter=icon)
