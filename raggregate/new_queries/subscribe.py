from raggregate.models.subscribe import Subscribe
from raggregate.models.submission import Submission
from raggregate.models.user import User
from raggregate.models.section import Section
import sqlahelper
from raggregate.new_queries import section as section_queries

import sqlalchemy

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

def get_subscription(user_id, section_id):
    return dbsession.query(Subscribe).filter(Subscribe.user_id == user_id).filter(Subscribe.section_id == section_id).one()

def get_base_subscriptions():
    return dbsession.query(Section.id).filter(Section.subscribe_by_default == True).all()

def get_subscribed_by_user_id(id):
    # Returns a list of section id's that this user is subscribed to
    # It has to generate one list from two data sources
    subscribed_to_list = []
    [subscribed_to_list.append(i[0]) for i in get_base_subscriptions()]
    user_subs = get_subs_by_user_id(id)
    for sub in user_subs:
        if sub.subscription_status and sub.section_id not in subscribed_to_list:
            subscribed_to_list.append(sub.section_id)
        elif not sub.subscription_status:
            if sub.section_id in subscribed_to_list:
                subscribed_to_list.remove(sub.section_id)
    return subscribed_to_list

def create_subscription(user_id, section_id, subscription_status):
    # if the given subscription already exists, update it instead
    # of creating another row in our many-to-many table.
    try:
        s = get_subscription(user_id, section_id)
        s.subscription_status = subscription_status
        dbsession.add(s)
    except sqlalchemy.orm.exc.NoResultFound:
        s = Subscribe(user_id, section_id, subscription_status)
        dbsession.add(s)
        dbsession.flush()
    return s
