from pyramid import testing
from raggregate.tests import BaseTest
from raggregate.queries import users
from raggregate.queries import submission as submission_queries
from raggregate.models.submission import Submission
from raggregate.queries import general
import re

class TestSubmissions(BaseTest):

    def create_submission(self, user = None, url = None, title = None, description = None):
        if not user:
            user = users.create_user(username = 'test', password = 'test')
        if not url:
            url = 'http://google.com'
        if not title:
            title = 'test'
        if not description:
            description = 'test'
        submission = Submission(title, description, url, user.id)
        self.dbsession.add(submission)
        self.dbsession.flush()
        return submission

    def test_create_submission(self):
        submission = self.create_submission()
        result = submission_queries.get_story_by_id(submission.id)
        assert submission.id == result.id

    def test_domain_parse(self):
        #@TODO: we should make this accept a fake user id in test mode at least
        # so that we don't have huge cascading failures if create_user is broken
        user = users.create_user(username = 't1', password = 'test')
        submission = self.create_submission(user = user, url = 'http://google.com')
        assert 'google.com' == submission.get_domain_name()

        user = users.create_user(username = 't2', password = 'test')
        submission = self.create_submission(user = user, url = 'http://googlewww.com')
        assert 'googlewww.com' == submission.get_domain_name()

        user = users.create_user(username = 't3', password = 'test')
        submission = self.create_submission(user = user, url = 'https://google.com')
        assert 'google.com' == submission.get_domain_name()

    def test_get_story_by_url_oldest(self):
        user01 = users.create_user(username = 't1', password = 'test')
        user02 = users.create_user(username = 't2', password = 'test')
        submission01 = self.create_submission(user = user01)
        submission02 = self.create_submission(user = user02)
        result = submission_queries.get_story_by_url_oldest('http://google.com')
        if result.__class__ == Submission:
            assert result.id == submission01.id
        else:
            assert False
