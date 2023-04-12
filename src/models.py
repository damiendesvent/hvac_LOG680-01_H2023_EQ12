
from sqlalchemy import Column, Integer, String, Float, DateTime, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

from datetime import *

def datetime_parser(o):
    if isinstance(o, datetime):
        return o.__str__()

class Event(Base):
    __tablename__ = "events"
    id = Column('id', VARCHAR(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    date = Column(DateTime(), nullable=False)
    nb_ticks = Column(Integer, nullable=False)
    event = Column(VARCHAR(length=15), nullable=False)
    data = Column(Float, nullable=False)

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()
        return self

    def __repr__(self):
        return f"Event  {self.id} {self.date} {self.data} {self.event} {self.nb_ticks}"
