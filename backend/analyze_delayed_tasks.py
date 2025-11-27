from database import get_db
from models import FactProyecto
from sqlalchemy import func

db = next(get_db())
projects = db.query(FactProyecto).filter(FactProyecto.tareas_retrasadas > 0).order_by(FactProyecto.tareas_retrasadas.desc()).limit(20).all()

with open("delayed_report.txt", "w") as f:
    f.write(f"Top 20 Projects with Delayed Tasks:\n")
    f.write(f"{'Project Name':<40} | {'Planned':<10} | {'Delayed':<10} | {'% Delayed':<10}\n")
    f.write("-" * 80 + "\n")

    for p in projects:
        planned = p.tareas_planificadas or 0
        delayed = p.tareas_retrasadas or 0
        pct = (delayed / planned * 100) if planned > 0 else 0
        f.write(f"{p.nombre[:40]:<40} | {planned:<10} | {delayed:<10} | {pct:.1f}%\n")

    # Aggregate stats
    total_planned = db.query(func.sum(FactProyecto.tareas_planificadas)).scalar() or 0
    total_delayed = db.query(func.sum(FactProyecto.tareas_retrasadas)).scalar() or 0
    f.write("-" * 80 + "\n")
    f.write(f"Total Portfolio: Planned={total_planned}, Delayed={total_delayed} ({total_delayed/total_planned*100:.1f}%)\n")
