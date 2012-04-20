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

class UserPicture(Base):
    __tablename__ = 'user_pictures'

    id = Column(GUID, primary_key=True)
    orig_filename = Column(UnicodeText)
    filename = Column(UnicodeText)
    file_hash = Column(UnicodeText)
    # 0 for user's computer
    # 1 for twitter
    # 2 for facebook
    source = Column(Integer, default=0)
    # @TODO: we should implement storage_schemes, etc., here.

    def __init__(self, orig_filename, filename, file_hash, source):
        self.orig_filename = orig_filename
        self.filename = filename
        self.file_hash = file_hash
        self.source = source

