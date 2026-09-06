"""
COSMOS Astrophysics Module: Atmospheric Biosignature Assessment
Evaluates multi-gas composition (H2O, CO2, CH4, O2, O3, CO, NH3, SO2), chemical disequilibrium,
stellar UV context, and abiotic false-positive pathways (e.g., O2 photolysis without H2O).
"""

import numpy as np
from typing import Dict, Any, List

TARGET_MOLECULES = ['H2O', 'CO2', 'CH4', 'O2', 'O3', 'CO', 'NH3', 'SO2']

def analyze_biosignature_composition(
    composition: Dict[str, float],
    equilibrium_temp_k: float = 288.0,
    stellar_uv_flux: float = 1.0
) -> Dict[str, Any]:
    """
    Performs comprehensive Atmospheric Biosignature Assessment.
    Returns biosignature indicator score, false positive risk assessment, and disequilibrium metrics.
    """
    cleaned_comp = {}
    for mol in TARGET_MOLECULES:
        val = float(composition.get(mol, composition.get(mol.lower(), 0.0)))
        cleaned_comp[mol] = max(0.0, val)

    o2_o3 = cleaned_comp['O2'] + (cleaned_comp['O3'] * 10.0)
    ch4 = cleaned_comp['CH4']
    co2 = cleaned_comp['CO2']
    h2o = cleaned_comp['H2O']

    # 1. Chemical Disequilibrium Assessment (O2/O3 + CH4 co-existence)
    disequilibrium_score = 0.0
    indicators = []
    false_positive_concerns = []

    if o2_o3 > 0.01 and ch4 > 0.0001:
        disequilibrium_score += 0.45
        indicators.append("Strong O2/O3 + CH4 Thermodynamic Disequilibrium Detected")
    elif o2_o3 > 0.05:
        disequilibrium_score += 0.25
        indicators.append("Elevated O2/O3 Abundance")

    if h2o > 0.005:
        disequilibrium_score += 0.25
        indicators.append("Water Vapor (H2O) Atmospheric Condensation Vector Detected")

    if ch4 > 0.001 and co2 > 0.01 and cleaned_comp['CO'] < 0.001:
        disequilibrium_score += 0.20
        indicators.append("CH4 + CO2 Enrichment with CO Depletion (Biogenic Biosignature Pattern)")

    # 2. Abiotic False Positive Analysis
    if o2_o3 > 0.05 and h2o < 0.0001:
        false_positive_concerns.append("High O2 without H2O: Risk of Desiccation/Ocean Loss Abiotic Photolysis")

    if stellar_uv_flux > 5.0 and o2_o3 > 0.02:
        false_positive_concerns.append("High Host Star UV Irradiation: CO2 Photolysis can synthesize abiotic O2/O3")

    if equilibrium_temp_k > 400.0:
        false_positive_concerns.append("High Equilibrium Temperature (>400K): Prevents stable liquid water reservoirs")

    confidence = round(float(np.clip(disequilibrium_score * 100, 5.0, 95.0)), 1)

    return {
        'status': 'Success',
        'assessment_label': 'Potential Atmospheric Biosignature Evidence' if disequilibrium_score >= 0.4 else 'Abiotic Atmospheric Composition',
        'biosignature_confidence_pct': confidence,
        'chemical_disequilibrium_index': round(float(disequilibrium_score), 3),
        'detected_indicators': indicators if indicators else ["Standard Atmospheric Equilibrium"],
        'false_positive_concerns': false_positive_concerns if false_positive_concerns else ["No Immediate Abiotic False-Positive Flags"],
        'composition_breakdown': cleaned_comp
    }
