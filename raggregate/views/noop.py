from pyramid.view import view_config

@view_config(renderer='buttons.mak', route_name='buttons')
def buttons(request):
    #just return
    return {}
