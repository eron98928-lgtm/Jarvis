from app.core import models, security
from app.core.database import SessionLocal, engine
import os
from dotenv import load_dotenv

load_dotenv()

def init():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create Admin (Eron)
    admin_username = os.getenv("ADMIN_NAME", "Eron")
    existing_admin = db.query(models.User).filter(models.User.username == admin_username).first()
    
    if not existing_admin:
        hashed_pw = security.get_password_hash("jarvis2026") # Default password, change on first login
        admin = models.User(
            username=admin_username,
            hashed_password=hashed_pw,
            access_level=2
        )
        db.add(admin)
        db.commit()
        print(f"Admin user '{admin_username}' created successfully.")
    else:
        print(f"Admin user '{admin_username}' already exists.")
    
    db.close()

if __name__ == "__main__":
    init()
