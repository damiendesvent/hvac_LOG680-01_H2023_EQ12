from src.models.models import Event

def get_event_by_date(date, db):
        return db.query(Event).filter(Event.date == date).first()

def get_all_events(db):
        return db.query(Event).all()