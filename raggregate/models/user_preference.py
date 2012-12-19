from raggregate.models import *

from sqlalchemy import Column
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from raggregate.models.user import User
from raggregate.guid_recipe import GUID


class UserPreference(Base):
    __tablename__ = 'user_preferences'
    id = Column(GUID, primary_key=True)
    user_id = Column(GUID, ForeignKey('users.id'))
    preference_list = Column(UnicodeText)

    user = relationship('User', backref='preferences')

    def __init__(self, user_id, preference_list):
        self.user_id = user_id
        self.preference_list = preference_list
