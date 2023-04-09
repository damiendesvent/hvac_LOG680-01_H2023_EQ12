from datetime import datetime, timedelta
from typing import List, Union
from pydantic import BaseModel

# We make a snapshot, and we save the cards in that snapshot on the specific column. The same card can be in multiple columns as cards can move
# from one column to another. We can also have a card in multiple snapshots, as a card can be moved from one snapshot to another.

class Base(BaseModel):
    id: str

    class Config:
        orm_mode = True

class Temperature(Base):
    date: datetime
    data: float

    class Config:
        orm_mode = True