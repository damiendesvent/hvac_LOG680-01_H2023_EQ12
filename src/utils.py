from src.models.models import Temperature

def get_temperature_by_date(date):
        return Temperature.query.filter_by(date=date).first()