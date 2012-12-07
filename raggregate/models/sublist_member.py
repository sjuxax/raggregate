from raggregate.models import *
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import UnicodeText
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from raggregate.guid_recipe import GUID

class SublistMember(Base):
    __tablename__ = 'sublists_members'
    id = Column(GUID, primary_key=True)
    sublist_id = Column(GUID, ForeignKey('sublists.id'))
    member_id = Column(GUID, ForeignKey('submissions.id'))
    added_by = Column(GUID, ForeignKey('users.id'))
    added_on = Column(DateTime)

    def __init__(self, sublist_id = None, member_id = None, added_by = None,
                  added_on = None):
        self.sublist_id = sublist_id
        self.member_id = member_id
        self.added_by = added_by
        self.added_on = added_on
