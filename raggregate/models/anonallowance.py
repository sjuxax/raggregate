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


#this table is a stopgap until we implement this kind of control in a good way
class AnonAllowance(Base):
    __tablename__ = 'anon_allow'

    id = Column(GUID, primary_key=True)
    permission = Column(UnicodeText)
    allowed = Column(Boolean, default=False)
