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
from sqlalchemy.schema import Table

from sqlalchemy.orm import relationship

from raggregate.guid_recipe import GUID

follows = Table('follows', Base.metadata,
                Column('follower', GUID, ForeignKey('users.id')),
                Column('followed', GUID, ForeignKey('users.id')),
               )

users_saves = Table('users_saves', Base.metadata,
                Column('user_id', GUID, ForeignKey('users.id')),
                Column('submission_id', GUID, ForeignKey('submissions.id')),
               )

class User(Base):
    __tablename__ = 'users'
    id = Column(GUID, primary_key=True)
    name = Column(Unicode(255), unique=True)
    password = Column(UnicodeText)
    email = Column(UnicodeText)
    real_name = Column(UnicodeText)
    temporary = Column(Boolean, default=False)
    about_me = Column(UnicodeText)
    picture = Column(GUID, ForeignKey('user_pictures.id'))
    karma = Column(Integer, default=0)
    notify_by_mail = Column(Boolean, default=True)
    twitter_origination = Column(Boolean, default=False)
    twitter_oauth_key = Column(UnicodeText)
    twitter_oauth_secret = Column(UnicodeText)
    facebook_origination = Column(Boolean, default=False)
    facebook_user_id = Column(UnicodeText)
    is_admin = Column(Boolean, default=False)
    lost_password_token = Column(GUID)
    password_token_claim_date = Column(DateTime(timezone=True))
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())
    added_by = Column(GUID)

    followed = relationship("User", secondary=follows, primaryjoin=id==follows.c.followed, secondaryjoin=id==follows.c.follower, backref="follows")
    saved = relationship("Submission", secondary=users_saves)
    picture_ref = relationship("UserPicture")

    def update_karma(self):
        #@TODO: find out if we want to allow negative general karma scores
        tally = 0
        try:
            for s in self.submissions:
                tally += s.points
        except:
            pass
        try:
            for c in self.comments:
                tally += c.points
        except:
            pass
        if self.karma != tally:
            self.karma = tally
        return tally

    def display_name(self):
        if self.real_name:
            return self.real_name
        else:
            return self.name

    # need an adaptable default picture getter method
    #def display_picture_filename(self):
    #    if self.picture_ref:
    #        return self.picture_ref.filename
    #    else:
    #        from raggregate import queries
    #        return queries.get_default_picture_filename()

    def hash_pw(self, pw):
        return crypt.encode(pw)

    def verify_pw(self, pw):
        return crypt.check(self.password, pw)

    def is_user_admin(self):
        # this is simplistic for now, but one day should use a real roles / permissions system
        return self.is_admin

    def is_user_notified(self, target_id):
        from raggregate.queries import notify
        return notify.is_user_notified(self.id, target_id)

    def __init__(self, name, password, email = None, real_name = None,
                  temporary = False, notify_by_mail = True):
        self.name = name
        self.password = self.hash_pw(password)
        self.email = email
        if real_name:
            self.real_name = real_name
        if temporary:
            self.temporary = True
        self.notify_by_mail = notify_by_mail
