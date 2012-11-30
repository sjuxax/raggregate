from pyramid import testing
from raggregate.tests import BaseTest
from raggregate.queries import users
from raggregate.queries import submission
from raggregate.models.submission import Submission
from raggregate.queries import general
import re

class TestSubmissions(BaseTest):

    def test_create_submission(self):
        #@TODO: another function that should be split out of the view for easy repitition.
        # if the view code changes substantially, this test will not keep up
        user = users.create_user(username = 'test', password = 'test')
        url = 'http://google.com'
        title = 'test'
        description = 'test'

        if url != '' and url is not None:
            url = general.strip_all_html(url)
            if not re.match(r'http[s]*:\/\/', url):
                url = 'http://' + url
        else:
            # set to None so that NULL goes into the database
            url = None

        sub = Submission(title, description, url, user.id)
        self.dbsession.add(sub)
        self.dbsession.flush()
        s = submission.get_story_by_id(sub.id)
        assert s.id == sub.id

    def test_domain_parse(self):
        title = 'test'
        description = 'test'
        #@TODO: we should make this accept a fake user id in test mode at least
        # so that we don't have huge cascading failures if create_user is broken
        user = users.create_user(username='test', password='test')

        sub = Submission(title, description, 'http://google.com', user.id)
        assert 'google.com' == sub.get_domain_name()

        sub = Submission(title, description, 'http://googlewww.com', user.id)
        assert 'googlewww.com' == sub.get_domain_name()

        sub = Submission(title, description, 'https://google.com', user.id)
        assert 'google.com' == sub.get_domain_name()
