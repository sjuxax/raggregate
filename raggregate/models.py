import transaction

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

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from sqlalchemy.event import listen

from sqlalchemy.schema import Table

from zope.sqlalchemy import ZopeTransactionExtension

import cryptacular.bcrypt

import uuid
import os
# for Python 3.x, this should be from urllib import parse
# however, that change should occur automatically with 2to3
import urlparse

import sqlahelper

DBSession = sqlahelper.get_session()
Base = declarative_base()

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

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
    twitter_origination = Column(Boolean, default=False)
    twitter_oauth_key = Column(UnicodeText)
    twitter_oauth_secret = Column(UnicodeText)
    facebook_origination = Column(Boolean, default=False)
    facebook_user_id = Column(UnicodeText)
    is_admin = Column(Boolean, default=False)
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

    def __init__(self, name, password, real_name = None, temporary = False):
        self.name = name
        self.password = self.hash_pw(password)
        if real_name:
            self.real_name = real_name
        if temporary:
            self.temporary = True

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(GUID, primary_key=True)
    title = Column(UnicodeText, nullable=False)
    description = Column(UnicodeText)
    points = Column(Integer)
    comment_tally = Column(Integer)
    category = Column(GUID)
    url = Column(UnicodeText)
    self_post = Column(Boolean)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())
    added_by = Column(GUID, ForeignKey('users.id'), nullable=False)
    deleted = Column(Boolean, default=False)
    invisible = Column(Boolean, default=False)
    hot_window_score = Column(Integer, default=None)
    hot_window_score_timestamp = Column(DateTime(timezone=True), default=None)
    downvote_tally = Column(Integer, default=None)
    downvote_tally_timestamp = Column(DateTime(timezone=True), default=None)
    upvote_tally = Column(Integer, default=None)
    upvote_tally_timestamp = Column(DateTime(timezone=True), default=None)
    total_vote_tally = Column(Integer)
    total_vote_timestamp = Column(DateTime(timezone=True), default=None)

    submitter = relationship("User", backref="submissions")
    votes = relationship("Vote", cascade="all, delete, delete-orphan")

    def __init__(self, title, description, url, user_id):
        self.title = title
        self.description = description
        self.url = url
        self.added_by = user_id

        if url is None:
            self.self_post = True
        else:
            self.self_post = False

    def tally_votes(self):
        votes = DBSession.query(Vote).filter(Vote.submission_id == self.id).filter(Vote.comment_id == None).all()
        tally = 0
        for v in votes:
            tally += v.points
        if self.points != tally:
            self.points = tally
        return votes

    def tally_comments(self):
        comments = DBSession.query(Comment).filter(Comment.submission_id == self.id).filter(Comment.body != '[deleted]').count()
        self.comment_tally = comments
        return comments

    def get_domain_name(self):
        if self.url:
            dn = urlparse.urlparse(self.url).netloc

            # replace preceding www. if it appears
            if 'www.' in dn[0:4]:
                dn = dn.replace('www.', '', 1)

            return dn
        else:
            return ''

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(GUID, primary_key=True)
    # we do not coalesce these into a generic item column
    # because things are easier/safer with the FK support.
    # the tradeoff here is size on various db structures.
    submission_id = Column(GUID, ForeignKey('submissions.id'))
    comment_id = Column(GUID, ForeignKey('comments.id'))
    user_id = Column(GUID, ForeignKey('users.id'), nullable=False)
    # points: -1 for down, 0 for neutral, 1 for up
    # this also allows easier manipulation of vote tallying if needed
    # considered using a boolean and deleting the row if a user unvotes
    # i guess but have no evidence that's slower than putting this back
    # to zero, and as above, makes it more difficult to "modify" the
    # voting system if needed.
    points = Column(Integer, nullable=False, default=0)
    # 0 for none, 1 for up, -1 for down
    direction = Column(Integer, nullable=False, default=0)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    voter = relationship("User", backref="votes")

    def __init__(self, item_id, user_id, points, target_type, comment_id = None):
        if target_type == 'comment':
            self.comment_id = comment_id
            self.submission_id = item_id
        elif target_type == 'submission':
            self.submission_id = item_id
        else:
            raise Exception("Need to know target type for this vote.")
        self.user_id = user_id
        self.points = points

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(GUID, primary_key=True)
    submission_id = Column(GUID, ForeignKey('submissions.id'), nullable=False)
    user_id = Column(GUID, ForeignKey('users.id'), nullable=False)
    parent_id = Column(GUID, nullable=False)
    in_reply_to = Column(GUID, ForeignKey('users.id'), nullable=True)
    body = Column(UnicodeText, nullable=False)
    points = Column(Integer, default=0)
    # unread field for epistle/mailbox display.
    unread = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    submitter = relationship("User", backref="comments", primaryjoin="User.id == Comment.user_id")
    recipient_u = relationship("User", primaryjoin="User.id == Comment.in_reply_to")
    votes = relationship("Vote", cascade="all, delete, delete-orphan")
    submission = relationship("Submission", backref="comments")

    def __init__(self, submission_id, user_id, parent_id, body, in_reply_to = None):
        self.submission_id = submission_id
        self.user_id = user_id
        self.parent_id = parent_id
        if body is None:
            raise Exception("Please include a message.")
        else:
            self.body = body
        self.in_reply_to = in_reply_to

    def tally_votes(self):
        votes = DBSession.query(Vote).filter(Vote.comment_id == self.id).all()
        tally = 0
        for v in votes:
            tally += v.points
        if self.points != tally:
            self.points = tally
        return votes

    def load_parent(self):
        # raggregate.queries depends on the models defined in this file
        # so it shouldn't be imported until it's ready to be used in a function
        # as it's being imported here. Otherwise, we die with dependency problems.
        # it is probably not advisable to do things this way, but it is much nicer
        from raggregate import queries
        if self.parent_id == None:
            print("No parent id on comment {0}, this is a problem...".format(self.id))
            return None
        p = queries.find_by_id(self.parent_id)
        return p

class Epistle(Base):
    __tablename__ = 'epistles'

    id = Column(GUID, primary_key=True)
    recipient = Column(GUID, ForeignKey('users.id'))
    sender = Column(GUID, ForeignKey('users.id'))
    body = Column(UnicodeText)
    subject = Column(UnicodeText)
    unread = Column(Boolean, default = True)
    #for threading
    parent = Column(GUID)
    # valid parent_types are 'epistle', 'story', 'comment'
    parent_type = Column(UnicodeText, default=u'epistle')
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    recipient_u = relationship("User", primaryjoin=("Epistle.recipient == User.id"))
    sender_u = relationship("User", primaryjoin=("Epistle.sender == User.id"))

    def __init__(self, recipient, sender, body, parent_type = None, parent = None, subject = None):
        self.recipient = recipient
        self.sender = sender
        self.body = body

        if parent_type is not None:
            self.parent_type = parent_type
        if parent is not None:
            self.parent = parent
        if subject is not None:
            self.subject = subject

    def display_subject(self):
        if self.subject is not None:
            return self.subject
        else:
            return u'<no subject>'

#this table is a stopgap until we implement this kind of control in a good way
class AnonAllowance(Base):
    __tablename__ = 'anon_allow'

    id = Column(GUID, primary_key=True)
    permission = Column(UnicodeText)
    allowed = Column(Boolean, default=False)

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

class Stat(Base):
    __tablename__ = 'stats'

    # this table is a k-v store for statistical information.
    key = Column(UnicodeText, primary_key=True)
    value = Column(UnicodeText)
    last_update = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    def __init__(self, key, value):
        self.key = key
        self.value = value

class Ban(Base):
    __tablename__ = 'bans'

    id = Column(GUID, primary_key=True)
    # 0 for IP, 1 for username, 2 for ip/username pair
    # left as integer for possible expansion
    ban_type = Column(Integer, default = 0)
    expires = Column(DateTime(timezone=True), default=None)
    # @FIXME: we should use INET from the PgSQL dialect after learning
    # how to fall back on other backends (hopefully smoother than GUID).
    # but in a hurry so just using UnicodeText for simplicity for now
    ip = Column(UnicodeText)
    duration = Column(UnicodeText)
    username = Column(UnicodeText)
    user_id = Column(GUID, ForeignKey('users.id'), default = None)
    added_by = Column(GUID, ForeignKey('users.id'), nullable=False)
    added_on = Column(DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    def __init__(self, ban_type = 0, ip = None, username = None, user_id = None, duration = None, added_by = None):
        from datetime import datetime
        self.ban_type = ban_type
        self.ip = ip
        self.username = username
        self.user_id = user_id
        if duration:
            self.expires = datetime.utcnow() + duration
            self.duration = str(duration)
        self.added_by = added_by

#def populate():
#    session = DBSession()
#    model = MyModel(name=u'root', value=55)
#    session.add(model)
#    session.flush()
#    transaction.commit()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    listen(sqlalchemy.orm.mapper, 'before_insert', make_uuid)
#    try:
#        populate()
#    except IntegrityError:
#        transaction.abort()

def initialize_sql_test(engine):
    DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    listen(sqlalchemy.orm.mapper, 'before_insert', make_uuid)
    return DBSession
#    try:
#        populate()
#    except IntegrityError:
#        transaction.abort()

def make_uuid(mapper, connection, target):
    if hasattr(target, 'id') and target.id is None:
        if type(mapper.columns.get('id').type) is GUID:
            target.id = uuid.UUID(bytes=os.urandom(16))
