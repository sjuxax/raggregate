from raggregate.queries import general
from pyramid.view import view_config
from raggregate.queries import users as user_queries

@view_config(route_name = 'lost_password', renderer='lost_password.mak')
def lost_password(request):
    get = request.GET

    if get and 'token' in get:
        token = get['token']
        user = user_queries.get_user_by_token(token)
        if user:
            # Make sure this token hasn't already been claimed
            if user.password_token_claim_date is not None:
                # This token has alread been claimed
                message = 'Not a valid token'
            else:
                user_queries.generate_new_password(request, user)
                message = 'Your request has been confirmed; please check mail for new password.'
        else:
            message = 'Not a valid token'
    else:
        message = 'Not a valid token'
    return {'message': message}
