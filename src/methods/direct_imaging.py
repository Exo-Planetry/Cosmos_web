import numpy as np
from typing import List, Dict, Any

def analyze_direct_imaging(intensity_values: List[float], signal_threshold: float = 1.2) -> Dict[str, Any]:
    """
    Analyzes direct coronagraphic imaging spatial signal intensities to detect companion exoplanet point sources.
    """
    if not intensity_values:
        raise ValueError("Intensity values list cannot be empty.")

    data = np.array(intensity_values, dtype=float)
    peak_signal = float(np.max(data))
    background_noise = float(np.mean(data))
    snr = float(peak_signal / (background_noise + 1e-6))

    is_confirmed = bool(peak_signal >= signal_threshold or snr > 3.0)

    return {
        'status': 'Success',
        'is_confirmed': is_confirmed,
        'metrics': {
            'peak_intensity': round(peak_signal, 3),
            'background_noise': round(background_noise, 3),
            'signal_to_noise_ratio': round(snr, 2)
        },
        'pixel_indices': list(range(len(data))),
        'intensity_values': data.tolist()
    }
