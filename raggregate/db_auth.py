from raggregate import queries

from pyramid.security import Everyone
from pyramid.security import Authenticated

class AuthPolicy(object):
    def authenticated_userid(self, request):
        if not request.session['users.id']:
            return None
        return queries.get_user_by_id(request.session['users.id'])

    def unauthenticated_userid(self, request):
        if not request.session['users.id']:
            return None
        return request.session['users.id']

    def effective_principals(self, request):
        effective_principals = [Everyone]
        s = request.session
        userid = self.unauthenticated_userid(request)
        if userid is None:
            return effective_principals
        #@TODO: Implement groups / moderation control
        groups = []
        if not self.authenticated_userid(request):
            return effective_principals
        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(groups)

        return effective_principles

    def remember(self, request, principal):
        request.session['users.id'] = principal
        request.session['logged_in'] = True

    def forget(self, request):
        del request.session['users.id']
        del request.session['logged_in']

