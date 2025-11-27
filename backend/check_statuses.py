from database import get_db
from models import FactProyecto, DimEstado
from sqlalchemy import func

db = next(get_db())
statuses = db.query(DimEstado.nombre_estado).distinct().all()
project_counts = db.query(DimEstado.nombre_estado, func.count(FactProyecto.proyecto_id))\
    .join(DimEstado, FactProyecto.estado_id == DimEstado.estado_id)\
    .group_by(DimEstado.nombre_estado).all()

print("Distinct Project Statuses in DB:")
for s in statuses:
    print(f"- {s[0]}")

print("\nProject Counts by Status:")
for s, count in project_counts:
    print(f"- {s}: {count}")
