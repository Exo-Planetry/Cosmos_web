"""
COSMOS ML Module: Unified Production Predictor & Explainable AI Service
Interfaces with Tabular Model C, False Positive Model B, 1D Transit Model A, and SHAP Explainer.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

from src.ml.tabular_model import TabularPlanetaryModel
from src.ml.false_positive import FalsePositiveClassifier
from src.ml.transit_model import TransitDetectionModel
from src.ml.explainability import SHAPExplainer
from src.utils.physics import calculate_multidimensional_esi

class ExoplanetInputSchema(BaseModel):
    pl_orbper: float = Field(365.25, gt=0, description="Orbital period in days")
    pl_rade: float = Field(1.0, gt=0, description="Planetary radius in Earth radii")
    pl_orbeccen: float = Field(0.0167, ge=0, le=0.99, description="Orbital eccentricity")
    pl_orbincl: float = Field(89.9, ge=0, le=180.0, description="Orbital inclination degrees")
    pl_tranmid: float = Field(2459000.0, description="Transit epoch midpoint JD")
    pl_imppar: float = Field(0.01, ge=0, description="Impact parameter")
    pl_trandep: float = Field(0.0084, gt=0, description="Transit depth fraction or ppm")
    pl_trandur: float = Field(13.0, gt=0, description="Transit duration in hours")
    pl_ratdor: float = Field(215.0, gt=0, description="Ratio of semi-major axis to stellar radius")
    pl_ratror: float = Field(0.0091, gt=0, description="Ratio of planet radius to stellar radius")
    sy_vmag: float = Field(4.83, description="Stellar V-band magnitude")
    sy_kmag: float = Field(3.28, description="Stellar K-band magnitude")

    @field_validator('pl_trandep')
    def check_trandep(cls, v):
        if v > 1.0:
            return v / 1.0e6
        return v

class ExoplanetPredictor:
    """Unified Multimodal ML Predictor Service."""

    FEATURE_NAMES = [
        'pl_orbper', 'pl_rade', 'pl_orbeccen', 'pl_orbincl',
        'pl_tranmid', 'pl_imppar', 'pl_trandep', 'pl_trandur',
        'pl_ratdor', 'pl_ratror', 'sy_vmag', 'sy_kmag'
    ]

    def __init__(self, model_path: str = 'models/tabular_model.joblib'):
        self.tabular_service = TabularPlanetaryModel(model_path=model_path)
        self.fp_service = FalsePositiveClassifier()
        self.transit_service = TransitDetectionModel()
        self.shap_explainer = SHAPExplainer(model_pipeline=self.tabular_service.pipeline)

    def predict(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates input, computes leak-free tabular prediction, SHAP attributions,
        false positive risk, multi-dimensional ESI, and candidate confidence status.
        """
        input_schema = ExoplanetInputSchema(**raw_input)
        df_input = pd.DataFrame([input_schema.model_dump()])[self.FEATURE_NAMES]

        # 1. Tabular Model C Prediction
        tabular_res = self.tabular_service.predict(df_input)
        candidate_prob = tabular_res['candidate_probability']

        # 2. False Positive Model B Classification
        fp_res = self.fp_service.classify(input_schema.model_dump())

        # 3. SHAP Explainability Feature Attributions
        shap_attributions = self.shap_explainer.explain_prediction(df_input, candidate_prob)

        # 4. Multi-dimensional ESI
        esi_details = calculate_multidimensional_esi(
            pl_rade=input_schema.pl_rade,
            pl_bmasse=input_schema.pl_rade ** 3.0,  # Approximate density mass scaling
            pl_eqt=288.0 * ((1.0 / (input_schema.pl_ratdor / 215.0)**2) ** 0.25) if input_schema.pl_ratdor > 0 else 288.0,
            st_flux=1.0 / (input_schema.pl_ratdor / 215.0)**2 if input_schema.pl_ratdor > 0 else 1.0,
            pl_orbper=input_schema.pl_orbper
        )

        # Candidate assessment terminology (Scientifically responsible)
        if candidate_prob >= 0.70 and fp_res['false_positive_risk_pct'] < 30.0:
            status_label = "HIGH-CONFIDENCE EXOPLANET CANDIDATE"
            class_color = "#00ffb3"
            is_confirmed_candidate = True
        elif candidate_prob >= 0.40:
            status_label = "POTENTIAL CANDIDATE (NEEDS FURTHER ANALYSIS)"
            class_color = "#ffb700"
            is_confirmed_candidate = False
        else:
            status_label = "PROBABLE FALSE POSITIVE / ECLIPSING BINARY"
            class_color = "#ff4757"
            is_confirmed_candidate = False

        return {
            'status': 'Success',
            'is_confirmed': is_confirmed_candidate,
            'candidate_probability_pct': round(candidate_prob * 100, 1),
            'confidence_score': round(candidate_prob * 100, 1),  # Backward compatibility
            'earth_similarity_index': esi_details['composite_esi'],
            'multidimensional_esi': esi_details,
            'classification_label': status_label,
            'label_color': class_color,
            'false_positive_analysis': fp_res,
            'xai_attributions': shap_attributions,
            'details': {
                'orbital_period_days': input_schema.pl_orbper,
                'planet_radius_earth': input_schema.pl_rade,
                'transit_depth': input_schema.pl_trandep,
                'transit_duration_hours': input_schema.pl_trandur
            }
        }
