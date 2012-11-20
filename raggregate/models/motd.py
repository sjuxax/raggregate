from raggregate.models import *
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import UnicodeText
from raggregate.guid_recipe import GUID

class MOTD(Base):
    __tablename__ = 'motd'
    id = Column(GUID, primary_key=True)
    message = Column(UnicodeText, nullable=False)
    author = Column(UnicodeText)
    source = Column(UnicodeText)
    link = Column(UnicodeText)
    added_by = Column(UnicodeText)
    datestring = Column(UnicodeText)

    def __init__(self, message = None, author = None, source = None, link = None,
                 added_by = None, datestring = None):
        self.message = message
        self.author = author
        self.source = source
        self.link = link
        self.added_by = added_by
        self.datestring = datestring
