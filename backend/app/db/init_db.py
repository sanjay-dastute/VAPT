from app.db.database import engine
from app.models import base, scan, vulnerability, user

def init_db():
    base.Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
