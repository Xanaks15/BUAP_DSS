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
def predict_defects(input_data: RayleighInput):
    # Map complexity to peak time factor (just an example heuristic)
    # In a real scenario, this would be calibrated.
    # Here we use the logic from the frontend: sigma = duration / 2.5
    sigma = input_data.duracionSemanas / 2.5
    
    # Estimate total defects based on complexity
    rates = {"baja": 0.03, "media": 0.05, "alta": 0.08}
    rate = rates.get(input_data.complejidad, 0.05)
    total_defects = int(input_data.horasEstimadas * rate)
    
    result = model.fit_predict(total_defects, sigma, input_data.duracionSemanas)
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
