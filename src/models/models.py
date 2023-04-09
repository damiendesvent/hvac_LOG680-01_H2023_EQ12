from sqlalchemy.sql.schema import ForeignKey

from sqlalchemy import Column, Boolean, String, Float, DateTime, VARCHAR
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
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


class Temperature(BaseModel):
    __tablename__ = "temperatures"
    date = Column(DateTime, default=datetime.utcnow)
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

    def add_card(self, card, db):
        self.cards.append(card)
        db.commit()
        db.refresh(self)
        return self

    def __repr__(self):
        return f"Column {self.name} ({self.id})"
