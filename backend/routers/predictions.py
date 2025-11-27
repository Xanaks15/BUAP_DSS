from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from prediction_model import model

router = APIRouter(
    prefix="/predictions",
    tags=["predictions"]
)

class PredictionRequest(BaseModel):
    total_defects: int
    peak_time: float # Week where max defects are expected
    duration_weeks: int

class PredictionResponse(BaseModel):
    sigma: float
    total_defects_estimated: int
    peak_week: float
    weekly_predictions: List[dict]

# Mock Auth Dependency
def verify_pm_role(x_role: Optional[str] = Header(None)):
    if x_role != "ProjectManager":
        raise HTTPException(status_code=403, detail="Access forbidden: Project Managers only")
    return x_role

@router.post("/predict", response_model=PredictionResponse)
def predict_defects(request: PredictionRequest, role: str = Depends(verify_pm_role)):
    """
    Generate defect prediction using Rayleigh model.
    Requires 'X-Role: ProjectManager' header.
    """
    if request.total_defects <= 0 or request.peak_time <= 0 or request.duration_weeks <= 0:
        raise HTTPException(status_code=400, detail="Invalid input parameters")
        
    result = model.fit_predict(
        total_defects=request.total_defects,
        peak_time=request.peak_time,
        duration_weeks=request.duration_weeks
    )
    return result
