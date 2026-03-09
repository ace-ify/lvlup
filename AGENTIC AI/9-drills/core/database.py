from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. The Database URL. 
# "sqlite:///./summarizer.db" means create a SQLite database file 
# called 'summarizer.db' right here in the root folder.
SQLALCHEMY_DATABASE_URL = "sqlite:///./summarizer.db"

# 2. The Engine. 
# This is the actual core connection to the database.
# (The connect_args check_same_thread=False is needed ONLY for SQLite in FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. The Session Local.
# Whenever a user makes a request to our API, we create a temporary "session" 
# to talk to the database, and close it when the request is done.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The Base.
# Later, when we create our Document model, it will inherit from this Base class.
# That tells SQLAlchemy: "Hey, take this Python class and turn it into a Database Table!"
Base = declarative_base()

# 5. Dependency helper function
# We will use this in our FastAPI endpoints to get a database session and close it automatically.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
