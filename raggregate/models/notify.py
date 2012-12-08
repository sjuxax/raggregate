from raggregate.models import *
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import UnicodeText
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from raggregate.guid_recipe import GUID

import datetime

class Notify(Base):
    __tablename__ = 'notifications'
    id = Column(GUID, primary_key=True)
    user_id = Column(GUID, ForeignKey('users.id'))
    target_id = Column(GUID)
    target_type = Column(UnicodeText)
    added_on = Column(DateTime)
    added_by = Column(GUID, ForeignKey('users.id'))

    def __init__(self, user_id = None, target_id = None, target_type = None,
                  added_on = None, added_by = None):
        self.user_id = user_id
        self.target_id = target_id
        self.target_type = target_type
        self.added_by = added_by

        if added_on:
            self.added_on = added_on
        else:
            self.added_on = datetime.datetime.utcnow()
