
from sqlalchemy import Column, Integer, String, Float, DateTime, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

from datetime import *

def datetime_parser(o):
    if isinstance(o, datetime):
        return o.__str__()

class BaseModel(Base):
    __abstract__ = True

    id = Column('id', VARCHAR(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)


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
        return f"{self.__class__.__name__}({self.id})"

class Event(BaseModel):
    __tablename__ = "events"
    date = Column(DateTime(), nullable=False)
    nb_ticks = Column(Integer, nullable=False)
    event = Column(VARCHAR(length=15), nullable=False)
    data = Column(Float, nullable=False)

    def __repr__(self):
        return f"Event  {self.id} {self.date} {self.data} {self.event} {self.nb_ticks}"


class Build(Base):
    __tablename__ = "builds"
    name = Column(VARCHAR(length=50), nullable=False, primary_key=True)
    version = Column(VARCHAR(length=50), nullable=False)
    size = Column(Integer, nullable=False)
    date = Column(DateTime(), nullable=False)

    def save(self, db):
        # if a record with the same name exists, update it
        if db.query(self.__class__).filter_by(name=self.name).first():
            db.merge(self)
        else:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def __repr__(self):
        return f"Build  {self.id} {self.name} {self.version} {self.size} {self.date}"
    
class Workflow(Base):
    __tablename__ = "workflows"
    name = Column(VARCHAR(length=50), nullable=False, primary_key=True)
    number_of_runs = Column(Integer, nullable=False)
    number_of_success = Column(Integer, nullable=False)
    number_of_failures = Column(Integer, nullable=False)

    def save(self, db):
        # if a record with the same name exists, update it
        if db.query(self.__class__).filter_by(name=self.name).first():
            db.merge(self)
        else:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def __repr__(self):
        return f"Workflow  {self.id} {self.name} {self.version} {self.size} {self.date}"