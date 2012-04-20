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

class Stat(Base):
    __tablename__ = 'stats'

    # this table is a k-v store for statistical information.
    key = Column(UnicodeText, primary_key=True)
    value = Column(UnicodeText)
    last_update = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    def __init__(self, key, value):
        self.key = key
        self.value = value
