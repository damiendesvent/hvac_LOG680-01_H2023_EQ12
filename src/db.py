import databases
import sqlalchemy

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

host = "labo3.brunomoya.com"
user = "root"
password = "Xln3I0us64"
db = "labo3"
port = "49165"

DATABASE_URL = f"mysql://{user}:{password}@{host}:{port}/{db}"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

print(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)