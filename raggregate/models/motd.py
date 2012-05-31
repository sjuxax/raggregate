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
    source_title = Column(UnicodeText)
    source_url = Column(UnicodeText)

    def __init__(self, message, author, added_by, datestring, source_title, source_url):
                 added_by = None):
        self.message = message
        self.author = author
        self.source = source
        self.link = link
        self.added_by = added_by
        self.datestring = datestring
        self.source_title = source_title
        self.source_url = source_url
