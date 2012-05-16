from raggregate.models import *
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from raggregate.guid_recipe import GUID

class Subscribe(Base):
    __tablename__ = 'subscribe'
    id = Column(GUID, primary_key=True)
    user_id = Column(GUID, ForeignKey('users.id'))
    section_id = Column(GUID, ForeignKey('sections.id'))
    subscription_status = Column(Boolean)

    def __init__(self, user_id = None, section_id = None, subscription_status = None):
        self.user_id = user_id
        self.section_id = section_id
        self.subscription_status = subscription_status
