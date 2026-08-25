import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

class ExoplanetInputSchema(BaseModel):
    pl_orbper: float = Field(..., gt=0, description="Orbital period in days")
    pl_rade: float = Field(..., gt=0, description="Planetary radius in Earth radii")
    pl_orbeccen: float = Field(0.0, ge=0, le=1.0, description="Orbital eccentricity")
    pl_orbincl: float = Field(89.5, ge=0, le=180.0, description="Orbital inclination degrees")
    pl_tranmid: float = Field(2459000.0, description="Transit epoch midpoint JD")
    pl_imppar: float = Field(0.0, ge=0, description="Impact parameter")
    pl_trandep: float = Field(..., gt=0, description="Transit depth fraction or ppm")
    pl_trandur: float = Field(..., gt=0, description="Transit duration in hours")
    pl_ratdor: float = Field(10.0, gt=0, description="Ratio of semi-major axis to stellar radius")
    pl_ratror: float = Field(0.1, gt=0, description="Ratio of planet radius to stellar radius")
    sy_vmag: float = Field(10.0, description="Stellar V-band magnitude")
    sy_kmag: float = Field(8.0, description="Stellar K-band magnitude")

    @field_validator('pl_trandep')

    def check_trandep(cls, v):
        # Convert ppm to fraction if value > 1.0
        if v > 1.0:
            return v / 1.0e6
        return v

class ExoplanetPredictor:
    """Production ML Predictor Service."""

    FEATURE_NAMES = [
        'pl_orbper', 'pl_rade', 'pl_orbeccen', 'pl_orbincl',
        'pl_tranmid', 'pl_imppar', 'pl_trandep', 'pl_trandur',
        'pl_ratdor', 'pl_ratror', 'sy_vmag', 'sy_kmag'
    ]

    def __init__(self, model_path: str = 'models/exoplanet_model.joblib'):
        self.model_path = model_path
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                artifact = joblib.load(self.model_path)
                self.pipeline = artifact['pipeline']
                print(f"[PREDICTOR] Successfully loaded model pipeline from {self.model_path}")
            except Exception as e:
                print(f"[PREDICTOR WARNING] Failed to load model artifact: {e}")
                self.pipeline = None
        else:
            print(f"[PREDICTOR WARNING] Model file {self.model_path} not found. Operating with physics fallback.")

    def predict(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validates input, runs ML prediction, and computes Earth Similarity Index."""
        # Convert and validate schema
        input_data = ExoplanetInputSchema(**raw_input)
        df_input = pd.DataFrame([input_data.model_dump()])[self.FEATURE_NAMES]

        if self.pipeline is not None:
            proba = float(self.pipeline.predict_proba(df_input)[0][1])
            is_confirmed = bool(proba >= 0.5)
        else:
            # Physical rule fallback if model file hasn't trained yet
            trandep = input_data.pl_trandep
            rade = input_data.pl_rade
            proba = min(0.99, max(0.01, (trandep * 100) + (1.0 if 0.5 <= rade <= 3.0 else 0.2)))
            is_confirmed = bool(proba >= 0.5)

        # Calculate ESI
        from src.utils.physics import calculate_esi
        esi_score = calculate_esi(input_data.pl_rade)

        # Classification label
        if is_confirmed:
            status_label = "CONFIRMED EXOPLANET CANDIDATE"
            class_color = "#00ffb3"
        elif proba >= 0.3:
            status_label = "POTENTIAL CANDIDATE (NEEDS FURTHER ANALYSIS)"
            class_color = "#ffb700"
        else:
            status_label = "FALSE POSITIVE / ECLIPSING BINARY"
            class_color = "#ff4757"

        return {
            'status': 'Success',
            'is_confirmed': is_confirmed,
            'confidence_score': round(proba * 100, 2),
            'earth_similarity_index': round(esi_score, 3),
            'classification_label': status_label,
            'label_color': class_color,
            'details': {
                'orbital_period_days': input_data.pl_orbper,
                'planet_radius_earth': input_data.pl_rade,
                'transit_depth': input_data.pl_trandep,
                'transit_duration_hours': input_data.pl_trandur
            }
        }
