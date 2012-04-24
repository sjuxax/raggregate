from raggregate.models import *
from raggregate.models.vote import Vote

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


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(GUID, primary_key=True)
    submission_id = Column(GUID, ForeignKey('submissions.id'), nullable=False)
    user_id = Column(GUID, ForeignKey('users.id'), nullable=False)
    parent_id = Column(GUID, nullable=False)
    in_reply_to = Column(GUID, ForeignKey('users.id'), nullable=True)
    body = Column(UnicodeText, nullable=False)
    points = Column(Integer, default=0)
    # unread field for epistle/mailbox display.
    unread = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    submitter = relationship("User", backref="comments", primaryjoin="User.id == Comment.user_id")
    recipient_u = relationship("User", primaryjoin="User.id == Comment.in_reply_to")
    votes = relationship("Vote", cascade="all, delete, delete-orphan")
    submission = relationship("Submission", backref="comments")

    def __init__(self, submission_id, user_id, parent_id, body, in_reply_to = None):
        self.submission_id = submission_id
        self.user_id = user_id
        self.parent_id = parent_id
        if body is None:
            raise Exception("Please include a message.")
        else:
            self.body = body
        self.in_reply_to = in_reply_to

    def tally_votes(self):
        votes = DBSession.query(Vote).filter(Vote.comment_id == self.id).all()
        tally = 0
        for v in votes:
            tally += v.points
        if self.points != tally:
            self.points = tally
        return votes

    def load_parent(self):
        # raggregate.queries depends on the models defined in this file
        # so it shouldn't be imported until it's ready to be used in a function
        # as it's being imported here. Otherwise, we die with dependency problems.
        # it is probably not advisable to do things this way, but it is much nicer
        from raggregate import queries
        if self.parent_id == None:
            print("No parent id on comment {0}, this is a problem...".format(self.id))
            return None
        p = queries.find_by_id(self.parent_id)
        return p

    def load_submission(self):
        from raggregate.new_queries import submission
        return submission.get_story_by_id(self.submission_id)

