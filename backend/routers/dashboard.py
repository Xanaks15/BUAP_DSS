from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from database import get_db
from models import FactProyecto, DimEstado, DimTipoProyecto, DimCliente, FactDefecto, DimTipoDefecto, DimFaseSDLC, DimTiempo

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/kpis/general")
def get_general_kpis(db: Session = Depends(get_db)):
    """
    Get high-level KPIs for the dashboard.
    """
    total_projects = db.query(func.count(FactProyecto.fact_id)).scalar()
    
    # ROI Average
    avg_roi = db.query(func.avg(FactProyecto.roi)).scalar() or 0.0
    
    # Total Profit
    total_profit = db.query(func.sum(FactProyecto.ganancia_proyecto)).scalar() or 0.0
    
    # Projects by Status
    status_counts = db.query(DimEstado.nombre_estado, func.count(FactProyecto.fact_id))\
        .join(FactProyecto, FactProyecto.estado_id == DimEstado.estado_id)\
        .group_by(DimEstado.nombre_estado).all()
        
    return {
        "total_projects": total_projects,
        "avg_roi": round(avg_roi, 2),
        "total_profit": round(total_profit, 2),
        "projects_by_status": {s: c for s, c in status_counts}
    }

@router.get("/projects/{project_id}/metrics")
def get_project_metrics(project_id: int, db: Session = Depends(get_db)):
    """
    Get specific metrics for a project: SPI, CPI, Risk, etc.
    """
    proj = db.query(FactProyecto).filter(FactProyecto.proyecto_id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Calculations
    # EV (Earned Value) approx = % Tasks Completed * Budget
    # This is a simplification. Ideally EV is sum of budget of completed tasks.
    # We'll use: (tareas_completadas / tareas_planificadas) * monto_planificado
    
    total_tasks = float(proj.tareas_planificadas or 1)
    completed_tasks = float(proj.tareas_completadas or 0)
    progress_pct = completed_tasks / total_tasks if total_tasks > 0 else 0
    
    pv = float(proj.monto_planificado or 0) # Planned Value (Budget)
    ac = float(proj.monto_real or 0)        # Actual Cost
    ev = pv * progress_pct                  # Earned Value
    
    spi = ev / pv if pv > 0 else 0 # Schedule Performance Index
    cpi = ev / ac if ac > 0 else 0 # Cost Performance Index
    
    # Risk Assessment
    # High Risk if SPI < 0.8 or CPI < 0.8
    risk_score = 0
    if spi < 0.8: risk_score += 1
    if cpi < 0.8: risk_score += 1
    
    retrasadas = float(proj.tareas_retrasadas or 0)
    if retrasadas > (total_tasks * 0.1): risk_score += 1
    
    risk_status = "Low"
    if risk_score == 1: risk_status = "Medium"
    elif risk_score >= 2: risk_status = "High"
    
    horas_trabajadas = float(proj.horas_trabajadas or 1)
    productivity = ev / horas_trabajadas if horas_trabajadas > 0 else 0
    
    return {
        "project_id": project_id,
        "name": proj.nombre,
        "spi": round(spi, 2),
        "cpi": round(cpi, 2),
        "ev": round(ev, 2),
        "pv": round(pv, 2),
        "ac": round(ac, 2),
        "risk_status": risk_status,
        "progress_pct": round(progress_pct * 100, 1),
        "productivity": round(productivity, 2) # Value per hour
    }

@router.get("/projects")
def get_projects_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get list of projects with key metrics.
    """
    projects = db.query(FactProyecto).offset(skip).limit(limit).all()
    return projects

@router.get("/projects/{project_id}/quality")
def get_project_quality(project_id: int, db: Session = Depends(get_db)):
    """
    Get quality metrics: Defects by severity, phase, density.
    """
    try:
        # Defects by Severity
        defects_severity = db.query(FactDefecto.severidad, func.count(FactDefecto.defecto_id))\
            .filter(FactDefecto.proyecto_id == project_id)\
            .group_by(FactDefecto.severidad).all()
            
        # Defects by Phase
        defects_phase = db.query(DimFaseSDLC.nombre_fase, func.count(FactDefecto.defecto_id))\
            .join(FactDefecto, FactDefecto.fase_id == DimFaseSDLC.fase_sdlc_id)\
            .filter(FactDefecto.proyecto_id == project_id)\
            .group_by(DimFaseSDLC.nombre_fase).all()
            
        # Total Defects
        total_defects = sum([c for _, c in defects_severity])
        
        # Defect Density (Defects / KLOC or Defects / Function Points)
        # We don't have size metrics, so we'll use Defects / 100 Hours as proxy
        proj = db.query(FactProyecto).filter(FactProyecto.proyecto_id == project_id).first()
        hours = proj.horas_trabajadas or 1
        density = (total_defects / hours) * 100
        
        # Defects by Week (for Rayleigh Curve)
        # Assuming DimTiempo has 'fecha'
        
        defects_by_week = db.query(func.week(DimTiempo.fecha), func.count(FactDefecto.defecto_id))\
            .join(FactDefecto, FactDefecto.tiempo_id == DimTiempo.tiempo_id)\
            .filter(FactDefecto.proyecto_id == project_id)\
            .group_by(func.week(DimTiempo.fecha))\
            .order_by(func.week(DimTiempo.fecha)).all()

        return {
            "total_defects": total_defects,
            "defect_density_per_100h": round(density, 2),
            "by_severity": {s: c for s, c in defects_severity},
            "by_phase": {p: c for p, c in defects_phase},
            "by_week": [{"week": w, "count": c} for w, c in defects_by_week]
        }
    except Exception as e:
        print(f"ERROR IN GET_PROJECT_QUALITY: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
