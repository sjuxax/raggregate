from pyramid import testing
from raggregate.tests import BaseTest
from raggregate.queries import epistle as epistle_queries
from raggregate.queries import users
from raggregate.models.epistle import Epistle
from raggregate.views.epistle import _unwrap_list

class TestEpistles(BaseTest):

    def create_epistle(self, recipient = None, sender = None, body = None, subject = None):
        if not recipient:
            recipient = users.create_user(username = 't1', password='test')
        if not sender:
            sender = users.create_user(username = 't2', password='test')
        if not body:
            body = u'test epistle'
        if not subject:
            subject = u'a simple test'
        epistle = Epistle(recipient.id, sender.id, body, subject = subject)
        self.dbsession.add(epistle)
        self.dbsession.flush()
        return epistle

    def test_get_epistle_by_id(self):
        epistle = self.create_epistle()
        result = epistle_queries.get_epistle_by_id(epistle.id)
        assert epistle.id == result.id

    def test_send_epistle_by_id(self):
        #@TODO: as this test illustrates, we should make a "send_epistle" function in queries
        u1 = users.create_user(username = 't1', password='test')
        u2 = users.create_user(username = 't2', password='test')
        ep = self.create_epistle(u1, u2, u'test epistle', subject = u'a simple test')
        epd = epistle_queries.get_epistle_by_recipient_id(u1.id)[0]
        assert ep.id == epd.id

    def test_unwrap_list_generator(self):
        test_list = [[[1]], [2], 3, [5], [[6]], [[9]]]
        ulist = []
        [ulist.append(e) for e in _unwrap_list(test_list)]
        assert ulist == [1, 2, 3, 5, 6, 9]

    def test_get_epistle_by_sender_id(self):
        epistle = self.create_epistle()
        result = epistle_queries.get_epistle_by_sender_id(epistle.sender)[0]
        assert epistle.id == result.id

    def test_get_epistle_by_sender_name(self):
        user = users.create_user(username = 'test', password = 'test')
        epistle = self.create_epistle(sender = user)
        result = epistle_queries.get_epistle_by_sender_name(user.name)[0]
        assert epistle.id == result.id

    def test_get_epistle_by_recipient_name(self):
        user = users.create_user(username = 'test', password = 'test')
        epistle = self.create_epistle(recipient = user)
        result = epistle_queries.get_epistle_by_recipient_name(user.name)[0]
        assert epistle.id == result.id

    def test_get_new_message_num(self):
        recipient = users.create_user(username = 'test', password = 'test')
        epistle = self.create_epistle(recipient = recipient)
        result = epistle_queries.get_new_message_num(recipient.id)
        assert result == 1

    def test_mark_epistle_read(self):
        #@TODO: Make query accept a dbsession variable so this can be tested
        #epistle = self.create_epistle()
        #epistle = epistle_queries.mark_epistle_read(epistle)
        #assert epistle.unread == False
        assert True

    def test_get_unread_epistles_by_recipient_id(self):
        epistle = self.create_epistle()
        result = epistle_queries.get_unread_epistles_by_recipient_id(epistle.recipient)[0]
        assert epistle.id == result.id
