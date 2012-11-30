from pyramid import testing
from raggregate.tests import BaseTest
from raggregate.queries import epistle as epistle_queries
from raggregate.queries import users
from raggregate.models.epistle import Epistle
from raggregate.views.epistle import _unwrap_list

class TestEpistles(BaseTest):

    def test_send_epistle_by_id(self):
        #@TODO: as this test illustrates, we should make a "send_epistle" function in queries
        u1 = users.create_user(username = 't1', password='test')
        u2 = users.create_user(username = 't2', password='test')
        ep = Epistle(u1.id, u2.id, u'test epistle', subject = u'a simple test')
        self.dbsession.add(ep)
        self.dbsession.flush()
        epd = epistle_queries.get_epistle_by_recipient_id(u1.id)[0]
        assert ep.id == epd.id

    def test_unwrap_list_generator(self):
        test_list = [[[1]], [2], 3, [5], [[6]], [[9]]]
        ulist = []
        [ulist.append(e) for e in _unwrap_list(test_list)]
        assert ulist == [1, 2, 3, 5, 6, 9]
