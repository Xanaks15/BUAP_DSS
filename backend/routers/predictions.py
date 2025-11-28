from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import FactProyecto, FactDefecto, DimTipoProyecto
from prediction_model import model
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
from sqlalchemy import func

router = APIRouter(
    prefix="/predictions",
    tags=["predictions"]
)

class RayleighInput(BaseModel):
    horasEstimadas: int
    duracionSemanas: int
    complejidad: str  # 'baja', 'media', 'alta'

class MonteCarloInput(BaseModel):
    horasEstimadas: int
    complejidad: str
    tipoProyecto: str = "Desarrollo Web"

@router.post("/rayleigh")
def predict_defects(input_data: RayleighInput, db: Session = Depends(get_db)):
    # Map complexity to peak time factor (just an example heuristic)
    # In a real scenario, this would be calibrated.
    # Here we use the logic from the frontend: sigma = duration / 2.5
    sigma = input_data.duracionSemanas / 2.5
    
    # 1. Calculate Historical Defect Rate
    # Strategy: 
    # - Try to find projects of the same 'tipoProyecto'
    # - Calculate sum(defects) / sum(hours)
    # - If no data, fallback to global average
    # - If still no data, fallback to complexity constants
    
    historical_rate = 0.0
    
    # Get Project Type ID if possible
    tipo_proj_id = db.query(DimTipoProyecto.tipo_proyecto_id)\
        .filter(DimTipoProyecto.nombre == input_data.tipoProyecto).scalar()
        
    query = db.query(
        func.sum(FactProyecto.horas_trabajadas).label("total_hours"),
        func.count(FactDefecto.defecto_id).label("total_defects")
    ).outerjoin(FactDefecto, FactProyecto.proyecto_id == FactDefecto.proyecto_id)
    
    if tipo_proj_id:
        query = query.filter(FactProyecto.tipo_proyecto_id == tipo_proj_id)
        
    result = query.first()
    
    if result and result.total_hours and result.total_hours > 0:
        # We have specific historical data
        historical_rate = result.total_defects / float(result.total_hours)
        print(f"DEBUG: Using Historical Rate for {input_data.tipoProyecto}: {historical_rate:.4f} (Defects: {result.total_defects}, Hours: {result.total_hours})")
    else:
        # Fallback: Global Average
        global_result = db.query(
            func.sum(FactProyecto.horas_trabajadas).label("total_hours"),
            func.count(FactDefecto.defecto_id).label("total_defects")
        ).outerjoin(FactDefecto, FactProyecto.proyecto_id == FactDefecto.proyecto_id).first()
        
        if global_result and global_result.total_hours and global_result.total_hours > 0:
            historical_rate = global_result.total_defects / float(global_result.total_hours)
            print(f"DEBUG: Using Global Historical Rate: {historical_rate:.4f}")
        else:
            # Fallback: Complexity Constants
            rates = {"baja": 0.03, "media": 0.05, "alta": 0.08}
            historical_rate = rates.get(input_data.complejidad, 0.05)
            print(f"DEBUG: Using Fixed Rate (No History): {historical_rate}")

    # Apply Complexity Factor to the Historical Rate
    # If complexity is 'alta', we might expect slightly more than average, 'baja' slightly less.
    # Simple heuristic adjustment:
    complexity_multipliers = {"baja": 0.8, "media": 1.0, "alta": 1.2}
    adjusted_rate = historical_rate * complexity_multipliers.get(input_data.complejidad, 1.0)
    
    total_defects = int(input_data.horasEstimadas * adjusted_rate)
    
    result = model.fit_predict(total_defects, sigma, input_data.duracionSemanas)
    
    # Inject the used rate into the result for transparency
    result["used_defect_rate"] = round(adjusted_rate, 5)
    result["data_source"] = "Historical Data" if (result and result.total_hours) else "Fixed Constants"
    
    return result

class EnhancedRayleighInput(RayleighInput):
    proyectoId: int = None # Optional, to fetch real KPIs if project exists

def get_historical_calibration(db: Session, project_type: str):
    """
    Get historical defect rate and average sigma (peak time) for a project type.
    """
    # 1. Defect Rate
    tipo_proj_id = db.query(DimTipoProyecto.tipo_proyecto_id)\
        .filter(DimTipoProyecto.nombre == project_type).scalar()
        
    query = db.query(
        func.sum(FactProyecto.horas_trabajadas).label("total_hours"),
        func.count(FactDefecto.defecto_id).label("total_defects")
    ).outerjoin(FactDefecto, FactProyecto.proyecto_id == FactDefecto.proyecto_id)
    
    if tipo_proj_id:
        query = query.filter(FactProyecto.tipo_proyecto_id == tipo_proj_id)
        
    result = query.first()
    
    historical_rate = 0.05 # Default fallback
    if result and result.total_hours and result.total_hours > 0:
        historical_rate = result.total_defects / float(result.total_hours)

    # 2. Average Sigma (Peak Time)
    # Heuristic: We don't store "peak time" directly, but we can approximate it 
    # if we had time-series data. For now, we'll use a heuristic based on project duration.
    # Or we could calculate the week with max defects for each project and average it.
    
    # Let's try to find the average week of max defects for past projects
    # This is complex in SQL. We'll stick to a simpler heuristic for now:
    # "Historical projects of this type usually peak at 40% of duration"
    historical_peak_ratio = 0.4 
    
    return historical_rate, historical_peak_ratio

def calculate_dynamic_adjustments(db: Session, project_id: int):
    """
    Calculate multipliers for K (Total Defects) and Sigma based on real KPIs.
    """
    if not project_id:
        return 1.0, 1.0, [], "No project ID provided. Using standard prediction."
        
    project = db.query(FactProyecto).filter(FactProyecto.proyecto_id == project_id).first()
    if not project:
        return 1.0, 1.0, [], "Project not found. Using standard prediction."
        
    k_multiplier = 1.0
    sigma_multiplier = 1.0
    explanations = []
    
    # 1. Tasks Delayed
    # If > 10% tasks are delayed, project is struggling. Increase K and Sigma.
    total_tasks = float(project.tareas_planificadas or 1)
    delayed_tasks = float(project.tareas_retrasadas or 0)
    delayed_pct = delayed_tasks / total_tasks
    
    if delayed_pct > 0.10:
        k_multiplier += 0.15
        sigma_multiplier += 0.10
        explanations.append(f"High task delay ({delayed_pct:.1%}) -> Increased expected defects (+15%) and delayed peak.")
        
    # 2. Productivity (EV / Hours Real)
    # If productivity is low, project takes longer, defects might spread out.
    # Assume standard productivity is around 1.0 (if EV and Hours are comparable units, which depends on implementation)
    # Let's use CPI instead as a proxy for efficiency: EV / AC
    ev = float(project.tareas_completadas or 0) / float(project.tareas_planificadas or 1) * float(project.monto_planificado or 0)
    ac = float(project.monto_real or 1)
    cpi = ev / ac if ac > 0 else 0
    
    if cpi < 0.85:
        sigma_multiplier += 0.15
        explanations.append(f"Low Cost Efficiency (CPI {cpi:.2f}) -> Curve flattened and peak delayed.")
        
    # 3. Critical Defects
    # If we already found many critical defects, the model should be more pessimistic.
    crit_defects = db.query(func.count(FactDefecto.defecto_id))\
        .join(DimTipoDefecto, FactDefecto.tipo_defecto_id == DimTipoDefecto.tipo_defecto_id)\
        .filter(FactDefecto.proyecto_id == project_id)\
        .filter(FactDefecto.severidad.in_(['Critico', 'Alta']))\
        .scalar() or 0
        
    if crit_defects > 5:
        k_multiplier += 0.20
        explanations.append(f"High volume of critical defects ({crit_defects}) -> Significantly increased total defect estimate.")

    # 4. Schedule Variance (Time)
    # Check if we are behind schedule
    # Simple check: Real Start vs Plan Start, or just use the delay days metric if available
    # We'll use a placeholder logic here assuming we could calculate 'days_late'
    # if days_late > 10: sigma_multiplier += 0.1
    
    if not explanations:
        explanations.append("Project is on track. Standard prediction applies.")
        
    return k_multiplier, sigma_multiplier, explanations, " | ".join(explanations)

def calculate_risk_index(k_mult, sigma_mult, explanations):
    # Base score 0 (Low Risk)
    score = 0
    
    # Deviations increase risk
    if k_mult > 1.0: score += (k_mult - 1.0) * 100 # e.g. 1.2 -> +20
    if sigma_mult > 1.0: score += (sigma_mult - 1.0) * 100
    
    # Critical keywords in explanations
    for exp in explanations:
        if "Critical" in exp: score += 30
        if "High task delay" in exp: score += 20
        
    # Cap at 100
    score = min(100, score)
    
    label = "Low"
    if score > 30: label = "Medium"
    if score > 60: label = "High"
    
    return score, label

@router.post("/rayleigh/enhanced")
def predict_defects_enhanced(input_data: EnhancedRayleighInput, db: Session = Depends(get_db)):
    """
    Enhanced Rayleigh Model with:
    1. Automatic Calibration (Historical Data)
    2. Dynamic Adjustments (Real-time KPIs)
    3. Risk Analysis
    """
    # 1. Base Parameters (Calibrated)
    hist_rate, hist_peak_ratio = get_historical_calibration(db, input_data.tipoProyecto)
    
    # Apply complexity factor to rate
    complexity_multipliers = {"baja": 0.8, "media": 1.0, "alta": 1.2}
    base_rate = hist_rate * complexity_multipliers.get(input_data.complejidad, 1.0)
    
    base_total_defects = int(input_data.horasEstimadas * base_rate)
    base_sigma = input_data.duracionSemanas / 2.5 # Default sigma
    
    # 2. Dynamic Adjustments (KPIs)
    k_mult, sigma_mult, explanations, explanation_text = calculate_dynamic_adjustments(db, input_data.proyectoId)
    
    # 3. Generate Curves
    # Standard (Original)
    original_curve = model.fit_predict(base_total_defects, base_sigma, input_data.duracionSemanas)
    
    # Enhanced (Adjusted)
    enhanced_curve = model.fit_predict_enhanced(
        base_total_defects, 
        base_sigma, 
        input_data.duracionSemanas,
        k_multiplier=k_mult,
        sigma_multiplier=sigma_mult
    )
    
    # 4. Risk Analysis
    risk_score, risk_label = calculate_risk_index(k_mult, sigma_mult, explanations)
    
    return {
        "original_prediction": original_curve,
        "enhanced_prediction": enhanced_curve,
        "adjustments": {
            "k_multiplier": round(k_mult, 2),
            "sigma_multiplier": round(sigma_mult, 2),
            "historical_rate_used": round(base_rate, 5)
        },
        "risk_analysis": {
            "score": int(risk_score),
            "level": risk_label,
            "explanation": explanation_text,
            "factors": explanations
        }
    }

@router.post("/monte-carlo")
def monte_carlo_simulation(input_data: MonteCarloInput, db: Session = Depends(get_db)):
    # 1. Get Historical Average Defects (Real Data from DW)
    # Filter by Project Type if provided
    query = db.query(
        FactProyecto.proyecto_id,
        func.count(FactDefecto.defecto_id).label("defect_count")
    ).outerjoin(FactDefecto, FactProyecto.proyecto_id == FactDefecto.proyecto_id)

    if input_data.tipoProyecto:
        query = query.join(DimTipoProyecto, FactProyecto.tipo_proyecto_id == DimTipoProyecto.tipo_proyecto_id)\
                     .filter(DimTipoProyecto.nombre == input_data.tipoProyecto)

    historical_query = query.group_by(FactProyecto.proyecto_id).all()
    
    if not historical_query:
        historical_avg = 0
    else:
        counts = [row.defect_count for row in historical_query]
        historical_avg = float(np.mean(counts))

    # 2. Run Simulation (5000 iterations)
    # Logic from generate_pmo_data.py:
    # lam = max(1, horas_plan/300) * random.uniform(0.8, 1.2)
    # defects = poisson(lam)
    
    n_simulations = 5000
    horas = input_data.horasEstimadas
    
    # Vectorized simulation
    # Base lambda
    base_lam = max(1, horas / 300.0)
    
    # Random factors (Uniform 0.8 to 1.2)
    factors = np.random.uniform(0.8, 1.2, n_simulations)
    
    # Lambdas for each scenario
    lambdas = base_lam * factors
    
    # Poisson samples
    simulated_defects = np.random.poisson(lambdas)
    
    return {
        "historical_average": round(historical_avg, 2),
        "distribution": simulated_defects.tolist(),
        "stats": {
            "mean": round(float(np.mean(simulated_defects)), 2),
            "min": int(np.min(simulated_defects)),
            "max": int(np.max(simulated_defects)),
            "p5": int(np.percentile(simulated_defects, 5)),
            "p95": int(np.percentile(simulated_defects, 95))
        }
    }
