import numpy as np
from typing import List, Dict, Any

def analyze_transit_photometry(
    light_curve_values: List[float],
    depth_threshold: float = 0.01,
    duration_threshold: float = 1.0
) -> Dict[str, Any]:
    """
    Analyzes transit light curve flux measurements and detects exoplanet dips.
    """
    if len(light_curve_values) < 3:
        raise ValueError("At least 3 light curve flux values are required.")

    flux_arr = np.array(light_curve_values, dtype=float)
    min_flux = float(np.min(flux_arr))
    max_flux = float(np.max(flux_arr))

    # Transit depth = baseline flux - minimum flux
    baseline = float(np.median(flux_arr))
    transit_depth = float(baseline - min_flux)

    # Transit duration = count of points significantly below baseline
    threshold_val = baseline - (transit_depth * 0.5)
    transit_duration_pts = int(np.sum(flux_arr < threshold_val))

    # Confirmation decision
    is_confirmed = bool(transit_depth >= depth_threshold and transit_duration_pts >= duration_threshold)

    time_pts = np.arange(len(flux_arr)).tolist()

    return {
        'status': 'Success',
        'is_confirmed': is_confirmed,
        'metrics': {
            'baseline_flux': round(baseline, 4),
            'transit_depth': round(transit_depth, 4),
            'transit_duration_points': transit_duration_pts,
            'min_flux': round(min_flux, 4)
        },
        'time_points': time_pts,
        'flux_values': flux_arr.tolist()
    }
