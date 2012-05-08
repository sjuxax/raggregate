from raggregate.models import *
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from raggregate.guid_recipe import GUID

class MOTD(Base):
    __tablename__ = 'motd'
    id = Column(GUID, primary_key=True)
    message = Column(UnicodeText, nullable=False)
    author = Column(UnicodeText)
    added_by = Column(UnicodeText)

    def __init__(self, message, author, added_by):
        self.message = message
        self.author = author
        self.added_by = added_by
