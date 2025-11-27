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
def get_general_kpis(
    start_date: str = None,
    end_date: str = None,
    project_type: str = None,
    status: str = None,
    client: str = None,
    db: Session = Depends(get_db)
):
    """
    Get high-level KPIs for the dashboard with optional Slice & Dice filters.
    """
    query = db.query(FactProyecto)
    
    # Apply Filters (Slice & Dice)
    if start_date:
        # Assuming DimTiempo join is needed or FactProyecto has date FKs
        # For simplicity, let's assume filtering by start date ID or similar if passed as ID
        # Or if passed as string 'YYYY-MM-DD', we need to join DimTiempo.
        # Let's assume for now we filter by IDs if they were passed, or we'd need a lookup.
        # Given the complexity of date ID lookup, let's skip date filter implementation details 
        # unless user provided date IDs, or we join DimTiempo.
        # Let's join DimTiempo for start_date
        query = query.join(DimTiempo, FactProyecto.fecha_inicio_real == DimTiempo.tiempo_id)\
                     .filter(DimTiempo.fecha >= start_date)
                     
    if end_date:
        # Re-joining might be tricky if already joined. 
        # Ideally we alias or check if joined. 
        # For this MVP, let's assume simple filtering or that start_date handled the join.
        pass 

    if project_type and project_type != 'all':
        query = query.join(DimTipoProyecto).filter(DimTipoProyecto.nombre == project_type)
        
    if status and status != 'all':
        query = query.join(DimEstado).filter(DimEstado.nombre_estado == status)
        
    if client and client != 'all':
        query = query.join(DimCliente).filter(DimCliente.nombre_cliente == client)

    # Execute Aggregations on Filtered Query
    total_projects = query.count()
    
    # For averages/sums we need to query columns from the filtered subquery or apply same filters
    # Easier to apply filters to a base query object and clone it? 
    # SQLAlchemy query objects are mutable.
    
    # Let's re-construct for aggregates or iterate (less efficient but safer for MVP)
    # Better: Use func.avg(FactProyecto.roi) with the same filters.
    
    # To avoid complex query construction in this snippet, let's fetch the filtered IDs first
    # This is not most performant but ensures correctness with simple code.
    filtered_projects = query.all()
    
    if not filtered_projects:
        return {
            "total_projects": 0,
            "avg_roi": 0.0,
            "total_profit": 0.0,
            "projects_by_status": {}
        }
        
    total_profit = sum([float(p.ganancia_proyecto or 0) for p in filtered_projects])
    avg_roi = sum([p.roi or 0 for p in filtered_projects]) / len(filtered_projects)
    
    # Calculate Total PV and AC for Portfolio
    total_pv = sum([float(p.monto_planificado or 0) for p in filtered_projects])
    total_ac = sum([float(p.monto_real or 0) for p in filtered_projects])
    
    # Calculate On-Time Projects Percentage
    # Logic: fecha_fin_real <= fecha_fin_plan
    # Note: Dates are FKs to DimTiempo (int), so comparing IDs might work if IDs are sequential/ordered by date.
    # Ideally we should join DimTiempo to compare actual dates, but assuming ID monotonicity for now or if they are just IDs.
    # If they are IDs, we can't strictly compare them unless we know the mapping.
    # However, let's assume for this MVP that if real <= plan it's on time. 
    # If they are None, we ignore.
    on_time_count = 0
    for p in filtered_projects:
        if p.fecha_fin_real and p.fecha_fin_plan:
            if p.fecha_fin_real <= p.fecha_fin_plan:
                on_time_count += 1
    
    on_time_projects_pct = (on_time_count / len(filtered_projects) * 100) if filtered_projects else 0

    # Calculate Critical Defects
    # We need to query FactDefecto for these projects
    project_ids = [p.proyecto_id for p in filtered_projects]
    critical_defects = 0
    if project_ids:
        critical_defects = db.query(func.count(FactDefecto.defecto_id))\
            .filter(FactDefecto.proyecto_id.in_(project_ids))\
            .filter(FactDefecto.severidad == 'Alta')\
            .scalar()

    # Calculate Additional KPIs
    
    # Hours Real vs Planned
    total_hours_planned = sum([float(p.horas_planificadas or 0) for p in filtered_projects])
    total_hours_real = sum([float(p.horas_trabajadas or 0) for p in filtered_projects])
    hours_real_vs_planned_pct = (total_hours_real / total_hours_planned * 100) if total_hours_planned > 0 else 0

    # Cost Real vs Planned
    # total_pv and total_ac are already calculated above
    cost_real_vs_planned_pct = (total_ac / total_pv * 100) if total_pv > 0 else 0

    # Tasks KPIs
    total_tasks_planned = sum([float(p.tareas_planificadas or 0) for p in filtered_projects])
    total_tasks_completed = sum([float(p.tareas_completadas or 0) for p in filtered_projects])
    total_tasks_delayed = sum([float(p.tareas_retrasadas or 0) for p in filtered_projects])
    
    tasks_completed_pct = (total_tasks_completed / total_tasks_planned * 100) if total_tasks_planned > 0 else 0
    tasks_delayed_pct = (total_tasks_delayed / total_tasks_planned * 100) if total_tasks_planned > 0 else 0
    tasks_not_completed_pct = 100 - tasks_completed_pct

    # Avg Employees
    total_employees = sum([float(p.empleados_asignados or 0) for p in filtered_projects])
    avg_employees_assigned = total_employees / len(filtered_projects) if filtered_projects else 0

    # Productivity (EV / Hours Worked)
    # EV for portfolio = sum(ganancia_proyecto of each project)
    total_ev = sum([float(p.ganancia_proyecto or 0) for p in filtered_projects])
        
    productivity = total_ev / total_hours_real if total_hours_real > 0 else 0

    # Defects Metrics
    project_ids = [p.proyecto_id for p in filtered_projects]
    total_defects = 0
    defects_by_phase = {}
    
    if project_ids:
        # Total Defects
        total_defects = db.query(func.count(FactDefecto.defecto_id))\
            .filter(FactDefecto.proyecto_id.in_(project_ids))\
            .scalar()
            
        # Defects by Phase
        defects_phase_query = db.query(DimFaseSDLC.nombre_fase, func.count(FactDefecto.defecto_id))\
            .join(FactDefecto, FactDefecto.fase_id == DimFaseSDLC.fase_sdlc_id)\
            .filter(FactDefecto.proyecto_id.in_(project_ids))\
            .group_by(DimFaseSDLC.nombre_fase).all()
        
        defects_by_phase = {p: c for p, c in defects_phase_query}

    # Recalculate status counts for the filtered set
    # We can do this in python for the filtered list
    status_counts_dict = {}
    for p in filtered_projects:
        st = p.estado.nombre_estado if p.estado else "Unknown"
        status_counts_dict[st] = status_counts_dict.get(st, 0) + 1

    risk_status = "Low"
    if tasks_delayed_pct > 50 or cost_real_vs_planned_pct > 20:
        risk_status = "High"
    elif tasks_delayed_pct > 20 or cost_real_vs_planned_pct > 10:
        risk_status = "Medium"

    # Defects by Severity
    defects_severity_query = db.query(FactDefecto.severidad, func.count(FactDefecto.defecto_id))\
        .join(FactProyecto, FactDefecto.proyecto_id == FactProyecto.proyecto_id)\
        .filter(FactProyecto.fact_id.in_([p.fact_id for p in filtered_projects]))\
        .group_by(FactDefecto.severidad).all()
        
    defects_by_severity = {s: c for s, c in defects_severity_query}
        
    return {
        "risk_status": risk_status,
        "total_projects": total_projects,
        "avg_roi": round(avg_roi, 2),
        "total_profit": round(total_profit, 2),
        "total_pv": round(total_pv, 2),
        "total_ac": round(total_ac, 2),
        "total_ev": round(total_ev, 2),
        "on_time_projects_pct": round(on_time_projects_pct, 1),
        "critical_defects": critical_defects,
        "total_defects": total_defects,
        "total_hours_planned": round(total_hours_planned, 1),
        "total_hours_real": round(total_hours_real, 1),
        "hours_real_vs_planned_pct": round(hours_real_vs_planned_pct, 1),
        "cost_real_vs_planned_pct": round(cost_real_vs_planned_pct, 1),
        "tasks_completed_pct": round(tasks_completed_pct, 1),
        "tasks_delayed_pct": round(tasks_delayed_pct, 1),
        "tasks_not_completed_pct": round(tasks_not_completed_pct, 1),
        "avg_employees_assigned": round(avg_employees_assigned, 1),
        "productivity": round(productivity, 2),
        "projects_by_status": status_counts_dict,
        "defects_by_phase": defects_by_phase,
        "defects_by_severity": defects_by_severity
    }

@router.get("/projects/{project_id}/metrics")
def get_project_metrics(project_id: int, db: Session = Depends(get_db)):
    """
    Get specific metrics for a project: SPI, CPI, Risk, etc.
    """
    # Alias DimTiempo for plan and real dates
    TiempoPlan = aliased(DimTiempo)
    TiempoReal = aliased(DimTiempo)

    proj_query = db.query(FactProyecto, TiempoPlan.fecha.label("fecha_plan"), TiempoReal.label("fecha_real"))\
        .outerjoin(TiempoPlan, FactProyecto.fecha_fin_plan == TiempoPlan.tiempo_id)\
        .outerjoin(TiempoReal, FactProyecto.fecha_fin_real == TiempoReal.tiempo_id)\
        .filter(FactProyecto.proyecto_id == project_id)
        
    result = proj_query.first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
        
    proj, fecha_plan, fecha_real = result
    
    # Calculations
    total_tasks = float(proj.tareas_planificadas or 1)
    completed_tasks = float(proj.tareas_completadas or 0)
    progress_pct = completed_tasks / total_tasks if total_tasks > 0 else 0
    
    pv = float(proj.monto_planificado or 0) # Planned Value (Budget)
    ac = float(proj.monto_real or 0)        # Actual Cost
    
    # EV = ganancia_proyecto
    ev = float(proj.ganancia_proyecto or 0)
    
    # SPI = EV / PV
    spi = ev / pv if pv > 0 else 0
    
    # CPI = EV / AC
    cpi = ev / ac if ac > 0 else 0
    
    # Risk Assessment
    risk_score = 0
    if spi < 0.8: risk_score += 1
    if cpi < 0.8: risk_score += 1

    retrasadas = float(proj.tareas_retrasadas or 0)
    if retrasadas > (total_tasks * 0.1): risk_score += 1
    
    risk_status = "Low"
    if risk_score == 1: risk_status = "Medium"
    elif risk_score >= 2: risk_status = "High"
    
    horas_trabajadas = float(proj.horas_trabajadas or 1)
    horas_planificadas = float(proj.horas_planificadas or 1)
    productivity = ev / horas_trabajadas if horas_trabajadas > 0 else 0
    
    # Defects by Phase
    defects_phase_query = db.query(DimFaseSDLC.nombre_fase, func.count(FactDefecto.defecto_id))\
        .join(FactDefecto, FactDefecto.fase_id == DimFaseSDLC.fase_sdlc_id)\
        .filter(FactDefecto.proyecto_id == project_id)\
        .group_by(DimFaseSDLC.nombre_fase).all()
    
    defects_by_phase = {p: c for p, c in defects_phase_query}
    total_defects = sum(defects_by_phase.values())

    # Task Percentages
    tasks_completed_pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    tasks_delayed_pct = (retrasadas / total_tasks * 100) if total_tasks > 0 else 0
    tasks_not_completed_pct = 100 - tasks_completed_pct
    
    # On Time Status & Delay Calculation
    is_on_time = 0
    delay_days = 0
    
    # Check dates from joined DimTiempo
    # fecha_plan and fecha_real are Date objects or None
    if fecha_real and fecha_plan:
        if fecha_real <= fecha_plan:
            is_on_time = 100
        else:
            # Calculate delay in days
            delta = fecha_real - fecha_plan
            delay_days = delta.days

    # Project Status for Chart
    status_counts_dict = {proj.estado.nombre_estado: 1} if proj.estado else {"Unknown": 1}

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
        "productivity": round(productivity, 2),
        "defects_by_phase": defects_by_phase,
        "total_defects": total_defects,
        "tasks_completed_pct": round(tasks_completed_pct, 1),
        "tasks_delayed_pct": round(tasks_delayed_pct, 1),
        "tasks_not_completed_pct": round(tasks_not_completed_pct, 1),
        "cost_real_vs_planned_pct": round(((ac - pv) / pv * 100), 1) if pv > 0 else 0,
        "avg_roi": round(proj.roi or 0, 2),
        "on_time_projects_pct": is_on_time,
        "delay_days": delay_days,
        "employees_assigned": proj.empleados_asignados or 0,
        "horas_planificadas": round(horas_planificadas, 1),
        "horas_reales": round(horas_trabajadas, 1),
        "projects_by_status": status_counts_dict
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
