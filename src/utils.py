from src.models.models import Temperature

def get_temperature_by_date(date, db):
        return db.query(Temperature).filter_by(date=date).first()