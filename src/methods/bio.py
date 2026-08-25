import numpy as np
from typing import Dict, Any

EARTH_ATMOSPHERE_BASELINE = {
    'Oxygen': 0.21,
    'Water': 0.01,
    'Nitrogen': 0.78,
    'CarbonDioxide': 0.0004,
    'Methane': 0.0000018
}

def analyze_biosignature_composition(composition: Dict[str, float]) -> Dict[str, Any]:
    """
    Evaluates atmospheric chemical composition against Earth biosignature benchmarks.
    """
    results = {}
    habitable_score = 0.0

    for element, baseline in EARTH_ATMOSPHERE_BASELINE.items():
        val = float(composition.get(element, 0.0))
        ratio = val / baseline if baseline > 0 else 0.0
        
        if element in ['Oxygen', 'Water']:
            if val > 0.05:
                habitable_score += 0.35
        elif element == 'Nitrogen':
            if val > 0.3:
                habitable_score += 0.2
        elif element == 'CarbonDioxide':
            if 0.0001 <= val <= 0.05:
                habitable_score += 0.1

        results[element] = {
            'observed_fraction': val,
            'earth_baseline': baseline,
            'status': 'Elevated' if val > baseline else ('Normal' if val == baseline else 'Depleted')
        }

    is_habitable = bool(habitable_score >= 0.5)

    return {
        'status': 'Success',
        'is_habitable': is_habitable,
        'biosignature_score': round(float(np.clip(habitable_score, 0.0, 1.0)), 2),
        'chemical_breakdown': results
    }
