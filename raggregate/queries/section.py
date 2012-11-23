from raggregate.models.submission import Submission
from raggregate.models.comment import Comment
from raggregate.models.vote import Vote
from raggregate.models.section import Section

import sqlahelper

dbsession = sqlahelper.get_session()

def get_sections(parent = None):
    if parent:
        r = dbsession.query(Section).filter(Section.parent == parent).all()
    else:
        r = dbsession.query(Section).filter(Section.parent == None).all()

    return r

def get_section_by_id(id):
    return dbsession.query(Section).filter(Section.id == id).one()

def get_section_by_name(name):
    return dbsession.query(Section).filter(Section.name == name).one()

