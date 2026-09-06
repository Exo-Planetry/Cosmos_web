"""
COSMOS Astrophysics Module: Transmission Spectroscopy Engine
Provides dual workflows:
1. Atmospheric Spectrum Simulator (Synthetic JWST NIRSpec/MIRI Opacity Model)
2. Observed Spectrum Analysis (Empirical Observational Transmission Spectrum)
"""

import numpy as np
from typing import Dict, Any, Optional, List

def simulate_transmission_spectrum(
    molecules: Optional[Dict[str, float]] = None,
    resolution: int = 100
) -> Dict[str, Any]:
    """
    Simulates synthetic transmission opacity spectrum across 0.6 - 12.0 microns.
    """
    if not molecules:
        molecules = {'H2O': 0.02, 'CO2': 0.01, 'CH4': 0.005, 'O3': 0.001, 'NH3': 0.0, 'SO2': 0.0}

    wavelengths = np.linspace(0.6, 12.0, resolution)
    baseline_ppm = 1000.0
    transit_depth_ppm = np.full_like(wavelengths, baseline_ppm)
    peaks = []

    # Gas absorption features
    if molecules.get('H2O', 0) > 0:
        band_depth = 250.0 * (molecules['H2O'] / 0.02)
        for center in [1.4, 1.9, 2.7, 6.0]:
            transit_depth_ppm += band_depth * np.exp(-((wavelengths - center) ** 2) / (2 * 0.15 ** 2))
            peaks.append({'molecule': 'H2O', 'wavelength_um': center, 'depth_ppm': round(baseline_ppm + band_depth, 1)})

    if molecules.get('CO2', 0) > 0:
        band_depth = 320.0 * (molecules['CO2'] / 0.01)
        transit_depth_ppm += band_depth * np.exp(-((wavelengths - 4.3) ** 2) / (2 * 0.20 ** 2))
        peaks.append({'molecule': 'CO2', 'wavelength_um': 4.3, 'depth_ppm': round(baseline_ppm + band_depth, 1)})

    if molecules.get('CH4', 0) > 0:
        band_depth = 180.0 * (molecules['CH4'] / 0.005)
        for center in [2.3, 3.3, 7.7]:
            transit_depth_ppm += band_depth * np.exp(-((wavelengths - 2.3) ** 2) / (2 * 0.18 ** 2))
            peaks.append({'molecule': 'CH4', 'wavelength_um': center, 'depth_ppm': round(baseline_ppm + band_depth, 1)})

    if molecules.get('O3', 0) > 0:
        band_depth = 210.0 * (molecules['O3'] / 0.001)
        transit_depth_ppm += band_depth * np.exp(-((wavelengths - 9.6) ** 2) / (2 * 0.25 ** 2))
        peaks.append({'molecule': 'O3', 'wavelength_um': 9.6, 'depth_ppm': round(baseline_ppm + band_depth, 1)})

    # Add Gaussian instrument noise
    np.random.seed(42)
    noise = np.random.normal(0, 15.0, size=resolution)
    measured_ppm = transit_depth_ppm + noise

    return {
        'status': 'Success',
        'spectrum_type': 'Atmospheric Spectrum Simulator (Synthetic Model)',
        'wavelengths_microns': [round(w, 2) for w in wavelengths.tolist()],
        'model_spectrum_ppm': [round(d, 1) for d in transit_depth_ppm.tolist()],
        'measured_spectrum_ppm': [round(d, 1) for d in measured_ppm.tolist()],
        'detected_peaks': peaks,
        'spectral_resolution_R': 300,
        'instrument_model': 'JWST NIRSpec / MIRI Synthetic Opacity'
    }

def analyze_observed_spectrum(
    wavelengths_um: List[float],
    depth_ppm: List[float],
    uncertainty_ppm: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Analyzes actual empirical observed transmission spectrum data.
    """
    w_arr = np.array(wavelengths_um, dtype=float)
    d_arr = np.array(depth_ppm, dtype=float)

    if uncertainty_ppm is None:
        err_str = "Uncertainty not available"
        u_arr = np.full_like(d_arr, np.nan)
    else:
        err_str = "Available"
        u_arr = np.array(uncertainty_ppm, dtype=float)

    peak_idx = np.argmax(d_arr)

    return {
        'status': 'Success',
        'spectrum_type': 'Observed Spectrum Analysis (Empirical Data)',
        'data_provenance': 'JWST/HST Target Transmission Spectroscopy Observation',
        'uncertainty_status': err_str,
        'wavelengths_microns': w_arr.tolist(),
        'transit_depth_ppm': d_arr.tolist(),
        'uncertainty_ppm': u_arr.tolist() if err_str == "Available" else None,
        'peak_feature_wavelength_um': round(float(w_arr[peak_idx]), 2),
        'max_depth_ppm': round(float(d_arr[peak_idx]), 1)
    }
