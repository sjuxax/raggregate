from raggregate.models import *

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

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(GUID, primary_key=True)
    # we do not coalesce these into a generic item column
    # because things are easier/safer with the FK support.
    # the tradeoff here is size on various db structures.
    submission_id = Column(GUID, ForeignKey('submissions.id'))
    comment_id = Column(GUID, ForeignKey('comments.id'))
    motd_id = Column(GUID, ForeignKey('motds.id'))
    user_id = Column(GUID, ForeignKey('users.id'), nullable=False)
    # points: -1 for down, 0 for neutral, 1 for up
    # this also allows easier manipulation of vote tallying if needed
    # considered using a boolean and deleting the row if a user unvotes
    # i guess but have no evidence that's slower than putting this back
    # to zero, and as above, makes it more difficult to "modify" the
    # voting system if needed.
    points = Column(Integer, nullable=False, default=0)
    # 0 for none, 1 for up, -1 for down
    direction = Column(Integer, nullable=False, default=0)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    voter = relationship("User", backref="votes")

    def __init__(self, item_id, user_id, points, target_type, comment_id = None):
        if target_type == 'comment':
            self.comment_id = comment_id
            self.submission_id = item_id
        elif target_type == 'submission':
            self.submission_id = item_id
        elif target_type == 'motd':
            self.motd_id = item_id
        else:
            raise Exception("Need to know target type for this vote.")
        self.user_id = user_id
        self.points = points
