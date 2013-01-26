from sqlalchemy import *
from migrate import *
from raggregate.guid_recipe import GUID


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    users = Table('users', meta, autoload=True)
    lost_password_token_column = Column('lost_password_token', GUID)
    password_token_claim_date_column = Column('password_token_claim_date',
                 DateTime(timezone=True))
    lost_password_token_column.create(users)
    password_token_claim_date_column.create(users)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    users = Table('users', meta, autoload=True)
    users.c.lost_password_token.drop()
    users.c.password_token_claim_date.drop()
