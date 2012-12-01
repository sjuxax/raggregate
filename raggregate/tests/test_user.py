from pyramid import testing
from raggregate.tests import BaseTest
from raggregate.queries import users
from raggregate.queries import general
from raggregate.models.user import User

class TestUsers(BaseTest):

    def create_user(self, username = None):
        if not username:
            username = 'test'
        user = users.create_user(username = username, password = username,)
        return user

    def test_create_user(self, username = None):
        u = self.create_user()
        res = self.dbsession.query(User).filter(User.name == u.name).first()
        assert res.id == u.id
        assert res.name == u.name

    def test_get_user_by_name(self):
        u = users.create_user(username = 'test', password='test')
        res = users.get_user_by_name(u.name)
        assert u.id == res.id

    def test_find_by_id_user(self):
        # depends on functional test_create_user
        u = users.create_user(username = 'test', password='test')
        res = general.find_by_id(u.id)
        assert res.id == u.id
        assert res.name == u.name

    def test_login_user(self):
        user = self.create_user()
        result = users.login_user(self.request, user, 'test')
        assert result

    def test_create_temp_user(self):
        temp_user = users.create_temp_user()
        assert temp_user.real_name == 'Unregistered User'
        assert temp_user.temporary
