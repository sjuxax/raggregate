from raggregate.models import *
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import UnicodeText
from raggregate.guid_recipe import GUID
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

class Sublist(Base):
    __tablename__ = 'sublists'
    id = Column(GUID, primary_key=True)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    visibility = Column(UnicodeText)
    added_by = Column(GUID, ForeignKey('users.id'))
    added_on = Column(DateTime)

    def __init__(self, title = None, description = None, visibility = None,
                 added_by = None, added_on = None):
        self.title = title
        self.description = description
        self.visibility = visibility
        self.added_by = added_by
        self.added_on = added_on
