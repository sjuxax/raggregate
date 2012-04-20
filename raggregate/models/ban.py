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

class Ban(Base):
    __tablename__ = 'bans'

    id = Column(GUID, primary_key=True)
    # 0 for IP, 1 for username, 2 for ip/username pair
    # left as integer for possible expansion
    ban_type = Column(Integer, default = 0)
    expires = Column(DateTime(timezone=True), default=None)
    # @FIXME: we should use INET from the PgSQL dialect after learning
    # how to fall back on other backends (hopefully smoother than GUID).
    # but in a hurry so just using UnicodeText for simplicity for now
    ip = Column(UnicodeText)
    duration = Column(UnicodeText)
    username = Column(UnicodeText)
    user_id = Column(GUID, ForeignKey('users.id'), default = None)
    added_by = Column(GUID, ForeignKey('users.id'), nullable=False)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    def __init__(self, ban_type = 0, ip = None, username = None, user_id = None, duration = None, added_by = None):
        from datetime import datetime
        self.ban_type = ban_type
        self.ip = ip
        self.username = username
        self.user_id = user_id
        if duration:
            self.expires = datetime.utcnow() + duration
            self.duration = str(duration)
        self.added_by = added_by
