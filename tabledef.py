from datetime import datetime
from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine("sqlite:///litecoinbot.db", echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    address = Column(String)

    def __init__(self, username, address):
        self.username = username
        self.address = address

class Tip(Base):
    __tablename__ = "tip"

    tip_id = Column(Integer, primary_key=True)
    sender = Column(String)
    recipient = Column(String)
    amount = Column(Float)
    status = Column(String)
    comment_id = Column(String)
    time_sent = Column(DateTime)

    def __init__(self, sender, recipient, amount, status, comment_id):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.status = status
        self.comment_id = comment_id
        self.time_sent = datetime.now()

# create tables
Base.metadata.create_all(engine)