import sqlalchemy
import sqlahelper
from raggregate.queries import users
from raggregate.queries import submission as submission_queries
from raggregate.models.sublist import Sublist
from raggregate.models.sublist_member import SublistMember

dbsession = sqlahelper.get_session()

def get_sublists():
    return dbsession.query(Sublist).all()

def get_sublist_by_title(title):
    return dbsession.query(Sublist).filter(Sublist.title == title).all()

def get_sublist_members(sublist_id):
    members = dbsession.query(SublistMember).filter(SublistMember.sublist_id == sublist_id).all()
    member_list = []
    for m in members:
        member_list.append(submission_queries.get_story_by_id(m.member_id))
    return member_list

def find_member_in_sublist(member_id, sublist_id):
    q = dbsession.query(SublistMember).filter(SublistMember.sublist_id == sublist_id)
    q = q.filter(SublistMember.member_id == member_id)
    return q.all()[0]

def remove_sublist_member(member_id, sublist_id):
    s = find_member_in_sublist(member_id, sublist_id)
    dbsession.delete(s)
    dbsession.flush()
    return True
