from src.models.models import Temperature

def get_temperature_by_date(date, db):
        return db.query(Temperature).filter(Temperature.date == date).first()

def get_all_temperatures(db):
        return db.query(Temperature).all()