from sqlalchemy import create_engine

def init_db():
    engine = create_engine('sqlite:///example.db')
    print("Database initialized with SQLAlchemy:", engine.url)
