from database import get_db
from models import FactProyecto

db = next(get_db())
count = db.query(FactProyecto).count()
print(f"Total Projects in DB: {count}")
