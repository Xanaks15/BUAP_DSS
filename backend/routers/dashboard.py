from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import func
from typing import List, Dict, Any
from database import get_db
from models import FactProyecto, DimEstado, DimTipoProyecto, DimCliente, FactDefecto, DimTipoDefecto, DimFaseSDLC, DimTiempo
import schemas

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
    try:
        # Alias DimTiempo for plan and real dates
        TiempoPlan = aliased(DimTiempo)
        TiempoReal = aliased(DimTiempo)

        # Query FactProyecto along with the actual dates
        query = db.query(FactProyecto, TiempoPlan.fecha.label("fecha_plan_date"), TiempoReal.fecha.label("fecha_real_date"))\
            .outerjoin(TiempoPlan, FactProyecto.fecha_fin_plan == TiempoPlan.tiempo_id)\
            .outerjoin(TiempoReal, FactProyecto.fecha_fin_real == TiempoReal.tiempo_id)
        
        # Apply Filters (Slice & Dice)
        if start_date:
            # Filter by start date (assuming fecha_inicio_real)
            TiempoInicio = aliased(DimTiempo)
            query = query.join(TiempoInicio, FactProyecto.fecha_inicio_real == TiempoInicio.tiempo_id)\
                         .filter(TiempoInicio.fecha >= start_date)
                         
        if end_date:
            pass 

        if project_type and project_type != 'all':
            query = query.join(DimTipoProyecto).filter(DimTipoProyecto.nombre == project_type)
            
        if status and status != 'all':
            query = query.join(DimEstado).filter(DimEstado.nombre_estado == status)
            
        if client and client != 'all':
            query = query.join(DimCliente).filter(DimCliente.nombre_cliente == client)

        # Fetch results
        results = query.all()
        
        total_projects = len(results)
        
        if total_projects == 0:
            return {
                "total_projects": 0,
                "avg_roi": 0.0,
                "total_profit": 0.0,
                "projects_by_status": {},
                "avg_delay_days": 0,
                "on_time_projects_pct": 0
            }
            
        # Aggregations
        total_profit = 0
        total_roi = 0
        total_pv = 0
        total_ac = 0
        total_ev = 0
        
        total_tasks_planned = 0
        total_tasks_completed = 0
        total_tasks_delayed = 0
        
        total_hours_planned = 0
        total_hours_real = 0
        total_employees = 0
        
        on_time_count = 0
        total_delay_days = 0
        
        project_ids = []
        status_counts_dict = {}

        for row in results:
            proj = row[0] # FactProyecto object
            f_plan = row.fecha_plan_date
            f_real = row.fecha_real_date
            
            project_ids.append(proj.proyecto_id)
            
            total_profit += float(proj.ganancia_proyecto or 0)
            total_roi += float(proj.roi or 0)
            
            pv = float(proj.monto_planificado or 0)
            ac = float(proj.monto_real or 0)
            total_pv += pv
            total_ac += ac
            
            # EV Calculation per project
            t_total = float(proj.tareas_planificadas or 1)
            t_done = float(proj.tareas_completadas or 0)
            prog = t_done / t_total if t_total > 0 else 0
            total_ev += prog * pv
            
            total_tasks_planned += t_total
            total_tasks_completed += t_done
            total_tasks_delayed += float(proj.tareas_retrasadas or 0)
            
            total_hours_planned += float(proj.horas_planificadas or 0)
            total_hours_real += float(proj.horas_trabajadas or 0)
            total_employees += float(proj.empleados_asignados or 0)
            
            # Status Count
            st = proj.estado.nombre_estado if proj.estado else "Unknown"
            status_counts_dict[st] = status_counts_dict.get(st, 0) + 1
            
            # Delay Calculation
            if f_real and f_plan:
                if f_real <= f_plan:
                    on_time_count += 1
                else:
                    delta = f_real - f_plan
                    total_delay_days += delta.days
        
        avg_roi = total_roi / total_projects
        avg_employees_assigned = total_employees / total_projects
        
        on_time_projects_pct = (on_time_count / total_projects * 100)
        avg_delay_days = total_delay_days / total_projects # Average delay across ALL projects
        
        hours_real_vs_planned_pct = ((total_hours_real - total_hours_planned) / total_hours_planned * 100) if total_hours_planned > 0 else 0
        cost_real_vs_planned_pct = ((total_ac - total_pv) / total_pv * 100) if total_pv > 0 else 0
        
        tasks_completed_pct = (total_tasks_completed / total_tasks_planned * 100) if total_tasks_planned > 0 else 0
        tasks_delayed_pct = (total_tasks_delayed / total_tasks_planned * 100) if total_tasks_planned > 0 else 0
        tasks_not_completed_pct = 100 - tasks_completed_pct
        
        productivity = total_ev / total_hours_real if total_hours_real > 0 else 0
        
        # Risk Status
        portfolio_spi = total_ev / total_pv if total_pv > 0 else 0
        portfolio_cpi = total_ev / total_ac if total_ac > 0 else 0
        
        risk_score = 0
        if portfolio_spi < 0.8: risk_score += 1
        if portfolio_cpi < 0.8: risk_score += 1
        
        risk_status = "Low"
        if risk_score == 1: risk_status = "Medium"
        elif risk_score >= 2: risk_status = "High"

        # Defects Metrics (Separate queries for efficiency)
        critical_defects = 0
        total_defects = 0
        defects_by_phase = {}
        defects_by_severity = {}
        
        if project_ids:
            critical_defects = db.query(func.count(FactDefecto.defecto_id))\
                .join(DimTipoDefecto, FactDefecto.tipo_defecto_id == DimTipoDefecto.tipo_defecto_id)\
                .filter(FactDefecto.proyecto_id.in_(project_ids))\
                .filter(FactDefecto.severidad.in_(['Critico', 'Alta']))\
                .scalar() or 0
                
            total_defects = db.query(func.count(FactDefecto.defecto_id))\
                .filter(FactDefecto.proyecto_id.in_(project_ids))\
                .scalar() or 0
                
            defects_phase_query = db.query(DimFaseSDLC.nombre_fase, func.count(FactDefecto.defecto_id))\
                .join(FactDefecto, FactDefecto.fase_id == DimFaseSDLC.fase_sdlc_id)\
                .filter(FactDefecto.proyecto_id.in_(project_ids))\
                .group_by(DimFaseSDLC.nombre_fase).all()
            defects_by_phase = {p: c for p, c in defects_phase_query}
            
            defects_severity_query = db.query(FactDefecto.severidad, func.count(FactDefecto.defecto_id))\
                .join(DimTipoDefecto, FactDefecto.tipo_defecto_id == DimTipoDefecto.tipo_defecto_id)\
                .filter(FactDefecto.proyecto_id.in_(project_ids))\
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
            "avg_delay_days": round(avg_delay_days, 1),
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/kpis/okrs")
def get_okr_metrics(db: Session = Depends(get_db)):
    """
    Get metrics for Balanced Scorecard with real data.
    """
    try:
        projects = db.query(FactProyecto).all()
        total_projects = len(projects)
        
        if total_projects == 0:
            return {}

        # --- Financial ---
        total_roi = sum(float(p.roi or 0) for p in projects)
        avg_roi = total_roi / total_projects
        
        # Cost Deviation: abs(AC - PV) / PV
        total_cost_dev_pct = 0
        profitable_count = 0
        
        for p in projects:
            pv = float(p.monto_planificado or 0)
            ac = float(p.monto_real or 0)
            if pv > 0:
                dev = abs(ac - pv) / pv * 100
                total_cost_dev_pct += dev
            
            if float(p.ganancia_proyecto or 0) > 0:
                profitable_count += 1
                
        avg_cost_dev = total_cost_dev_pct / total_projects
        profitable_pct = (profitable_count / total_projects) * 100

        # --- Customer ---
        # Re-query with joins for dates
        TiempoPlan = aliased(DimTiempo)
        TiempoReal = aliased(DimTiempo)
        
        projects_dates = db.query(FactProyecto, TiempoPlan.fecha, TiempoReal.fecha)\
            .outerjoin(TiempoPlan, FactProyecto.fecha_fin_plan == TiempoPlan.tiempo_id)\
            .outerjoin(TiempoReal, FactProyecto.fecha_fin_real == TiempoReal.tiempo_id)\
            .all()
            
        on_time_count = 0
        acceptable_delay_count = 0
        
        for p, d_plan, d_real in projects_dates:
            if d_real and d_plan:
                if d_real <= d_plan:
                    on_time_count += 1
                    acceptable_delay_count += 1
                else:
                    delay_days = (d_real - d_plan).days
                    if delay_days <= 20:
                        acceptable_delay_count += 1
        
        on_time_pct = (on_time_count / total_projects) * 100
        acceptable_delay_pct = (acceptable_delay_count / total_projects) * 100
        
        # Defect Free (Critical)
        project_ids = [p.proyecto_id for p in projects]
        projects_with_crit_defects = db.query(FactDefecto.proyecto_id).distinct()\
            .filter(FactDefecto.proyecto_id.in_(project_ids))\
            .filter(FactDefecto.severidad.in_(['Critico', 'Alta'])).all()
        projects_with_crit_defects_ids = {p[0] for p in projects_with_crit_defects}
        
        crit_defect_free_count = total_projects - len(projects_with_crit_defects_ids)
        crit_defect_free_pct = (crit_defect_free_count / total_projects) * 100

        # --- Internal Process ---
        total_defects_count = db.query(func.count(FactDefecto.defecto_id)).scalar() or 0
        avg_defects = total_defects_count / total_projects
        
        total_tasks_plan = sum(p.tareas_planificadas or 0 for p in projects)
        total_tasks_done = sum(p.tareas_completadas or 0 for p in projects)
        tasks_completed_pct = (total_tasks_done / total_tasks_plan * 100) if total_tasks_plan > 0 else 0
        
        # New Metric: Critical Defects % (Goal < 5%)
        critical_defects_count = db.query(func.count(FactDefecto.defecto_id))\
            .filter(FactDefecto.severidad.in_(['Critico', 'Alta'])).scalar() or 0
        critical_defects_pct = (critical_defects_count / total_defects_count * 100) if total_defects_count > 0 else 0

        # --- Learning ---
        total_ev_val = 0
        total_ac_val = sum(float(p.monto_real or 0) for p in projects)
        
        for p in projects:
            pv = float(p.monto_planificado or 0)
            t_tot = float(p.tareas_planificadas or 1)
            t_done = float(p.tareas_completadas or 0)
            prog = t_done / t_tot if t_tot > 0 else 0
            total_ev_val += prog * pv
            
        cpi_pct = (total_ev_val / total_ac_val * 100) if total_ac_val > 0 else 0
        model_usage_pct = 65 

        return {
            "financial": {
                "roi": round(avg_roi, 1),
                "cost_dev": round(avg_cost_dev, 1),
                "profitable_projects_pct": round(profitable_pct, 1)
            },
            "customer": {
                "on_time_pct": round(on_time_pct, 1),
                "defect_free_pct": round(crit_defect_free_pct, 1),
                "acceptable_delay_pct": round(acceptable_delay_pct, 1)
            },
            "internal": {
                "avg_defects": round(avg_defects, 1),
                "tasks_completed_pct": round(tasks_completed_pct, 1),
                "critical_defects_pct": round(critical_defects_pct, 1)
            },
            "learning": {
                "productivity_pct": round(cpi_pct, 1),
                "model_usage_pct": model_usage_pct
            }
        }
    except Exception as e:
        print(f"Error in get_okr_metrics: {str(e)}")
        return {}

@router.get("/projects", response_model=List[schemas.ProyectoBase])
def get_projects_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get list of projects with key metrics.
    """
    projects = db.query(FactProyecto).options(joinedload(FactProyecto.tipo_proyecto)).offset(skip).limit(limit).all()
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
