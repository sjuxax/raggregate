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

class Section(Base):
    __tablename__ = 'sections'

    id = Column(GUID, primary_key=True)
    name = Column(UnicodeText)
    description = Column(UnicodeText)
    subscribe_by_default = Column(Boolean, default=False)
    parent = Column(GUID, ForeignKey('sections.id'), nullable=True)
    added_by = Column(GUID, ForeignKey('users.id'), nullable=False)
    enabled = Column(Boolean, default=True)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())
    modified_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())
    picture = Column(GUID, ForeignKey('section_pictures.id'))

    stories = relationship("Submission", backref="sections")
    picture_ref = relationship("SectionPicture")

    def __init__(self, name = None, description = None, parent = None, added_by = None, modified_on = None, subscribe_by_default = False, enabled = True):
        self.name = name
        self.description = description
        self.parent = parent
        self.added_by = added_by
        self.modified_on = modified_on
        self.subscribe_by_default = subscribe_by_default
        self.enabled = enabled

