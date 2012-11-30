from pyramid import testing
from raggregate.tests import BaseTest
from raggregate.queries import users
from raggregate.queries import general
from raggregate.models.user import User

class TestUsers(BaseTest):

    def test_create_user(self, username = None):
        if not username:
            username = 'test'
        u = users.create_user(username = username, password = username,)
        res = self.dbsession.query(User).filter(User.name == username).first()
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
