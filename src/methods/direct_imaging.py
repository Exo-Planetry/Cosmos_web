"""
COSMOS Astrophysics Module: Coronagraphic Direct Imaging Analysis
Calculates background spatial noise standard deviation (sigma_bg), background-subtracted
peak PSF companion signal, and signal-to-noise ratio (SNR).
"""

import numpy as np
from typing import List, Dict, Any, Optional

def analyze_direct_imaging(
    intensity_values: List[float],
    background_region: Optional[List[float]] = None,
    signal_threshold_snr: float = 4.0,
    is_simulation: bool = True
) -> Dict[str, Any]:
    """
    Analyzes direct spatial intensity array (2D flattened or 1D radial scan).
    Uses background region standard deviation for science-grade SNR calculation.
    """
    if not intensity_values:
        raise ValueError("Intensity values array cannot be empty.")

    data = np.array(intensity_values, dtype=float)

    # 1. Background Estimation
    if background_region and len(background_region) >= 3:
        bg_data = np.array(background_region, dtype=float)
        bg_mean = float(np.mean(bg_data))
        bg_std = float(np.std(bg_data))
    else:
        # Estimate background from lower 50th percentile of image intensity
        median_val = np.median(data)
        bg_mask = data <= median_val
        bg_mean = float(np.mean(data[bg_mask]))
        bg_std = float(np.std(data[bg_mask]))

    if bg_std < 1e-9:
        bg_std = 1e-6

    # 2. Peak Signal Detection & Background Subtraction
    peak_raw = float(np.max(data))
    peak_idx = int(np.argmax(data))
    signal_net = peak_raw - bg_mean

    # 3. Science-Grade Signal-to-Noise Ratio (SNR)
    snr = float(signal_net / bg_std)

    is_confirmed = bool(snr >= signal_threshold_snr and signal_net > 0)

    return {
        'status': 'Success',
        'data_source_type': 'Simulation' if is_simulation else 'Observed Coronagraphic Data',
        'is_confirmed': is_confirmed,
        'metrics': {
            'peak_intensity_raw': round(peak_raw, 4),
            'peak_intensity_subtracted': round(signal_net, 4),
            'background_mean': round(bg_mean, 4),
            'background_noise_std': round(bg_std, 4),
            'signal_to_noise_ratio': round(snr, 2),
            'detected_pixel_index': peak_idx
        },
        'pixel_indices': list(range(len(data))),
        'intensity_values': data.tolist(),
        'background_subtracted_intensity': (data - bg_mean).tolist()
    }
