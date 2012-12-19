import json

import sqlalchemy
import sqlahelper

from raggregate.models.user import User
from raggregate.models.user_preference import UserPreference

dbsession = sqlahelper.get_session()


def get_user_prefs(user_id):
    """
    Retrieve JSON object of user preferences from the database and return as a dictionary.

        Arguments:
        user_id -- The ID of the user whose preferences you want to retrieve
    """
    try:
        prefs = dbsession.query(UserPreference).filter(UserPreference.user_id == user_id).one()
        return json.loads(prefs.preference_list)
    except sqlalchemy.orm.exc.NoResultFound:
        return {}


def set_user_prefs(user_id, user_prefs):
    """
    Save dictionary of preferences to the database as a JSON object.

        Arguments:
        user_id     -- The ID of the user whose preferences you want to set
        user_prefs  -- A dictionary of user preferences
    """
    try:
        prefs = dbsession.query(UserPreference).filter(UserPreference.user_id == user_id).one()
        prefs.preference_list = json.dumps(user_prefs)
    except sqlalchemy.orm.exc.NoResultFound:
        prefs = UserPreference(user_id, json.dumps(user_prefs))

    dbsession.add(prefs)
    dbsession.flush()
