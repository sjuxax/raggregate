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

class Epistle(Base):
    __tablename__ = 'epistles'

    id = Column(GUID, primary_key=True)
    recipient = Column(GUID, ForeignKey('users.id'))
    sender = Column(GUID, ForeignKey('users.id'))
    body = Column(UnicodeText)
    subject = Column(UnicodeText)
    unread = Column(Boolean, default = True)
    #for threading
    parent = Column(GUID)
    # valid parent_types are 'epistle', 'story', 'comment'
    parent_type = Column(UnicodeText, default=u'epistle')
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    recipient_u = relationship("User", primaryjoin=("Epistle.recipient == User.id"))
    sender_u = relationship("User", primaryjoin=("Epistle.sender == User.id"))

    def __init__(self, recipient, sender, body, parent_type = None, parent = None, subject = None):
        self.recipient = recipient
        self.sender = sender
        self.body = body

        if parent_type is not None:
            self.parent_type = parent_type
        if parent is not None:
            self.parent = parent
        if subject is not None:
            self.subject = subject

    def display_subject(self):
        if self.subject is not None:
            return self.subject
        else:
            return u'<no subject>'
