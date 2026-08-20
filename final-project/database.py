from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

DATABASE_URL = "mysql+pymysql://root:04122007@localhost:3306/finalproject"

engine = create_engine(DATABASE_URL)

LocalSession = sessionmaker(autoflush=False,autocommit = False,bind=engine)

Base = declarative_base()

def get_db():
    db = LocalSession()
    try: 
        yield db
    finally:
        db.close()

