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
