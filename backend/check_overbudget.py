from database import get_db
from models import FactProyecto

db = next(get_db())
overbudget_projects = db.query(FactProyecto).filter(FactProyecto.monto_real > FactProyecto.monto_planificado).all()

if overbudget_projects:
    print(f"Found {len(overbudget_projects)} projects over budget:")
    for p in overbudget_projects:
        diff = p.monto_real - p.monto_planificado
        pct = (diff / p.monto_planificado) * 100 if p.monto_planificado else 0
        print(f"- {p.nombre}: Real=${p.monto_real:,.2f} vs Plan=${p.monto_planificado:,.2f} (Excess: ${diff:,.2f}, +{pct:.1f}%)")
else:
    print("No projects found where actual cost exceeds planned cost.")
