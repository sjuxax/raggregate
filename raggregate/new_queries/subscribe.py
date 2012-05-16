from raggregate.models.subscribe import Subscribe
from raggregate.models.submission import Submission
from raggregate.models.user import User
from raggregate.models.section import Section
import sqlahelper
from raggregate.new_queries import section as section_queries

dbsession = sqlahelper.get_session()

def get_subs():
    # Returns all subscriptions as a list of subscription objects
    return dbsession.query(Subscribe).all()

def get_subs_by_user_id(id):
    # Returns a list of subscription objects filtered by user id
    return dbsession.query(Subscribe).filter(Subscribe.user_id == id).all()

def get_subs_by_section_id(id):
    # Returns a list of subscription objects filtered by section id
    return dbsession.query(Subscribe).filter(Subscribe.section_id == id).all()

def get_subscribe_to_by_user_id(id):
    # Returns a list of section id's that this user is subscribed to
    # It has to generate one list from two data sources
    subscribed_to_list = []
    user_subs = get_subs_by_user_id(id)
    sections = section_queries.get_sections()
    for sec in sections:
        if sec.subscribe_by_default:
            subscribed_to_list.append(sec.id)
    for sub in user_subs:
        if sub.subscription_status == True:
            subscribed_to_list.append(sub.section_id)
        else:
            if sub.section_id in subscribed_to:
                subscribed_to_list.remove(sub.section_id)
    return subscribed_to_list
