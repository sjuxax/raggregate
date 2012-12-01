from raggregate.models import *
from raggregate.models.vote import Vote
from raggregate.models.comment import Comment

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import DateTime
from sqlalchemy import text
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey

from raggregate.guid_recipe import GUID

import urlparse

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(GUID, primary_key=True)
    title = Column(UnicodeText, nullable=False)
    description = Column(UnicodeText)
    points = Column(Integer)
    comment_tally = Column(Integer)
    category = Column(GUID)
    url = Column(UnicodeText)
    self_post = Column(Boolean)
    slug = Column(UnicodeText, unique=True)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())
    added_by = Column(GUID, ForeignKey('users.id'), nullable=False)
    deleted = Column(Boolean, default=False)
    invisible = Column(Boolean, default=False)
    hot_window_score = Column(Integer, default=None)
    hot_window_score_timestamp = Column(DateTime(timezone=True), default=None)
    downvote_tally = Column(Integer, default=None)
    downvote_tally_timestamp = Column(DateTime(timezone=True), default=None)
    upvote_tally = Column(Integer, default=None)
    upvote_tally_timestamp = Column(DateTime(timezone=True), default=None)
    total_vote_tally = Column(Integer)
    total_vote_timestamp = Column(DateTime(timezone=True), default=None)
    section = Column(GUID, ForeignKey('sections.id'), nullable=True)
    render_type = Column(UnicodeText, default='story_md')

    submitter = relationship("User", backref="submissions")
    votes = relationship("Vote", cascade="all, delete, delete-orphan")

    def __init__(self, title, description, url, user_id, slug = None, section = None,
                 render_type = None):
        self.title = title
        self.description = description
        self.url = url
        self.added_by = user_id
        self.slug = slug
        self.section = section
        self.render_type = render_type

        if url is None:
            self.self_post = True
        else:
            self.self_post = False

    def tally_votes(self):
        votes = DBSession.query(Vote).filter(Vote.submission_id == self.id).filter(Vote.comment_id == None).all()
        tally = 0
        for v in votes:
            tally += v.points
        if self.points != tally:
            self.points = tally
        return votes

    def tally_comments(self):
        comments = DBSession.query(Comment).filter(Comment.submission_id == self.id).filter(Comment.body != '[deleted]').count()
        self.comment_tally = comments
        return comments

    def get_domain_name(self):
        if self.url:
            dn = urlparse.urlparse(self.url).netloc

            # replace preceding www. if it appears
            if 'www.' in dn[0:4]:
                dn = dn.replace('www.', '', 1)

            return dn
        else:
            return ''

