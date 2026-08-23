from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from setting import settings
DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)

LocalSession = sessionmaker(autoflush=False,autocommit = False,bind=engine)

Base = declarative_base()

def get_db():
    db = LocalSession()
    try: 
        yield db
    finally:
        db.close()

