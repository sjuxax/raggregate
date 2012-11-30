import unittest
from pyramid import testing
from sqlalchemy import create_engine

def _initTestingDB():
    from raggregate.models import initialize_sql_test
    r = initialize_sql_test(create_engine('sqlite://'))
    session, base = r[0], r[1]
    return session

class BaseTest(object):

    def setup(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        self.config.scan('raggregate.models')
        self.initTestingDB()

    def tearDown(self):
        testing.tearDown()

    def initTestingDB(self):
        self.dbsession = _initTestingDB()
