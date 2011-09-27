import unittest
from pyramid.config import Configurator
from pyramid import testing

from raggregate import queries
from raggregate.models import User
from raggregate.models import Epistle
from raggregate.models import Submission

import re

def _initTestingDB():
    from sqlalchemy import create_engine
    from raggregate.models import initialize_sql_test
    session = initialize_sql_test(create_engine('sqlite://'))
    return session

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.dbsession = _initTestingDB()

    def tearDown(self):
        testing.tearDown()

class TestUsers(BaseTest):
    def test_create_user(self, username = None):
        if not username:
            username = 'test'
        u = queries.create_user(username = username, password = username,)
        res = self.dbsession.query(User).filter(User.name == username).first()
        self.assertEqual(res.id, u.id)
        self.assertEqual(res.name, u.name)

    def test_get_user_by_name(self):
        u = queries.create_user(username = 'test', password='test')
        res = queries.get_user_by_name(u.name)
        self.assertEqual(u.id, res.id)

    def test_find_by_id_user(self):
        # depends on functional test_create_user
        u = queries.create_user(username = 'test', password='test')
        res = queries.find_by_id(u.id)
        self.assertEqual(res.id, u.id)
        self.assertEqual(res.name, u.name)

class TestEpistles(BaseTest):
    def test_send_epistle_by_id(self):
        #@TODO: as this test illustrates, we should make a "send_epistle" function in queries
        u1 = queries.create_user(username = 't1', password='test')
        u2 = queries.create_user(username = 't2', password='test')
        ep = Epistle(u1.id, u2.id, u'test epistle', subject = u'a simple test')
        self.dbsession.add(ep)
        self.dbsession.flush()
        epd = queries.get_epistle_by_recipient_id(u1.id)[0]
        self.assertEqual(ep.id, epd.id)

class TestSubmissions(BaseTest):
    def test_create_submission(self):
        #@TODO: another function that should be split out of the view for easy repitition.
        # if the view code changes substantially, this test will not keep up
        user = queries.create_user(username = 'test', password = 'test')
        url = 'http://google.com'
        title = 'test'
        description = 'test'

        if url != '' and url is not None:
            url = queries.strip_all_html(url)
            if not re.match(r'http[s]*:\/\/', url):
                url = 'http://' + url
        else:
            # set to None so that NULL goes into the database
            url = None

        sub = Submission(title, description, url, user.id)
        self.dbsession.add(sub)
        self.dbsession.flush()
        s = queries.get_story_by_id(sub.id)
        self.assertEqual(s.id, sub.id)
