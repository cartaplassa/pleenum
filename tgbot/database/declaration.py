from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, DateTime, Integer, create_engine
from datetime import datetime
import os 


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_FILENAME = 'main.db'
connection_string = "sqlite:///" + os.path.join(BASE_DIR, DB_FILENAME)
Base = declarative_base()
engine = create_engine(connection_string, echo=True)
Session = sessionmaker()

# These constants are used on db creation. Recreate db to apply changes.
USERNAME_MAXLENGTH = 64
PLEENUMNAME_MAXLENGTH = 64


class User(Base):
    __tablename__ = 'users'
    telegram_id = Column(Integer(), primary_key=True)
    user_name = Column(String(USERNAME_MAXLENGTH), nullable=False)
    pleenums_created = Column(Integer(), default=0)

    def __repr__(self):
        return f"<User id={self.telegram_id}, name=\"{self.user_name}\">"


class Pleenum(Base):
    __tablename__ = 'pleenums'
    id = Column(Integer(), primary_key=True)
    name = Column(String(PLEENUMNAME_MAXLENGTH), nullable=False)
    chat_id = Column(Integer(), nullable=False)
    creator_id = Column(Integer(), nullable=False)
    created_time = Column(DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Pleenum #{self.id}: \"{self.name}\">\n<Created by \"{self.creator_id}\" in chat {self.chat_id}>"

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer(), primary_key=True)
    pleenum_id = Column(Integer(), nullable=False)
    member_id = Column(Integer(), nullable=False)

    def __repr__(self):
        return f"<Membership of user {self.member_id} in {self.pleenum_id}>"
