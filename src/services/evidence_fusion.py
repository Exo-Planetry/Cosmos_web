"""
COSMOS Core Engine: Candidate Assessment & Multi-Modal Evidence Fusion Engine
Synthesizes independent observational & theoretical evidence vectors:
1. Transit Photometry Evidence (%)
2. Radial Velocity Orbital Consistency (%)
3. Atmospheric Spectral Evidence (%)
4. Coronagraphic Imaging Evidence (%)
5. Physical & Dynamical Consistency (%)
6. Habitability Radiative Context (%)
7. False-Positive Risk Factor (%)
8. Data Provenance Quality Index

Calculates an overall Candidate Assessment Score (0 - 100).
Clearly framed as a scientific assessment score, NOT a claim of planet confirmation.
"""

import numpy as np
from typing import Dict, Any, Optional

def compute_evidence_fusion(
    transit_confidence_pct: float = 85.0,
    rv_consistency_pct: float = 80.0,
    atmospheric_evidence_pct: float = 60.0,
    imaging_evidence_pct: float = 20.0,
    physical_consistency_pct: float = 90.0,
    habitability_context_pct: float = 75.0,
    false_positive_risk_pct: float = 12.0,
    data_quality_label: str = "High (NASA Archive Validated)"
) -> Dict[str, Any]:
    """
    Computes weighted multi-modal Candidate Assessment Score out of 100.
    """
    # Weight factors
    w_transit = 0.30
    w_rv = 0.20
    w_physical = 0.15
    w_fp = 0.15  # Penalty weight
    w_atmos = 0.10
    w_hz = 0.10

    raw_score = (
        (transit_confidence_pct * w_transit) +
        (rv_consistency_pct * w_rv) +
        (physical_consistency_pct * w_physical) +
        (atmospheric_evidence_pct * w_atmos) +
        (habitability_context_pct * w_hz) -
        (false_positive_risk_pct * w_fp * 1.5)
    )

    assessment_score = int(np.clip(round(raw_score), 5, 99))

    # Qualitative candidate tier
    if assessment_score >= 80:
        tier_label = "STRONG EXOPLANET CANDIDATE"
        tier_color = "#00ffb3"
    elif assessment_score >= 55:
        tier_label = "MODERATE CANDIDATE (REQUIRING FOLLOW-UP OBSERVATIONS)"
        tier_color = "#ffb700"
    else:
        tier_label = "LOW CONFIDENCE / SUSPECTED FALSE POSITIVE"
        tier_color = "#ff4757"

    return {
        'status': 'Success',
        'candidate_assessment_score': assessment_score,
        'candidate_tier_label': tier_label,
        'tier_color': tier_color,
        'scientific_disclaimer': "This score is a multi-evidence analytical assessment index (0-100), NOT a claim of scientific discovery or confirmed planet status.",
        'evidence_breakdown': {
            'transit_photometry_confidence': f"{round(transit_confidence_pct, 1)}%",
            'orbital_rv_consistency': f"{round(rv_consistency_pct, 1)}%",
            'physical_dynamical_consistency': f"{round(physical_consistency_pct, 1)}%",
            'atmospheric_spectral_evidence': f"{round(atmospheric_evidence_pct, 1)}%",
            'habitability_context_score': f"{round(habitability_context_pct, 1)}%",
            'direct_imaging_evidence': f"{round(imaging_evidence_pct, 1)}%",
            'false_positive_risk': f"{round(false_positive_risk_pct, 1)}%",
            'data_quality_index': data_quality_label
        },
        'formula_weights': {
            'transit_weight': "30%",
            'rv_weight': "20%",
            'physical_consistency_weight': "15%",
            'false_positive_penalty': "-22.5%",
            'atmospheric_weight': "10%",
            'habitability_weight': "10%"
        }
    }
