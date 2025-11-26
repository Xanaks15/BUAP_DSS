import numpy as np
from scipy.stats import rayleigh
from typing import List, Dict, Any

class RayleighModel:
    def __init__(self):
        pass

    def fit_predict(self, total_defects: int, peak_time: float, duration_weeks: int) -> Dict[str, Any]:
        """
        Predict defect discovery rate using Rayleigh distribution.
        
        PDF: f(t) = (t / sigma^2) * exp(-t^2 / (2*sigma^2))
        CDF: F(t) = 1 - exp(-t^2 / (2*sigma^2))
        
        In Software Engineering (Putnam model):
        Defects(t) = K * (1 - exp(-t^2 / (2*Tm^2)))
        where K = total defects, Tm = peak time (time of max defect discovery).
        
        Sigma in scipy.stats.rayleigh is related to Tm.
        Mode of Rayleigh is sigma. So Tm = sigma.
        """
        sigma = peak_time
        
        weeks = np.arange(1, duration_weeks + 1)
        
        # Calculate cumulative defects at each week
        # CDF of Rayleigh at t is 1 - exp(-t^2 / 2sigma^2)
        # We multiply by total_defects (K)
        
        cumulative_prob = rayleigh.cdf(weeks, scale=sigma)
        cumulative_defects = total_defects * cumulative_prob
        
        # Defects found per week (discrete approximation)
        defects_per_week = np.diff(cumulative_defects, prepend=0)
        
        return {
            "sigma": sigma,
            "total_defects_estimated": total_defects,
            "peak_week": peak_time,
            "weekly_predictions": [
                {"week": int(w), "defects": round(d, 2), "cumulative": round(c, 2)}
                for w, d, c in zip(weeks, defects_per_week, cumulative_defects)
            ]
        }

model = RayleighModel()
