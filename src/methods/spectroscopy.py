"""
COSMOS Astrophysics Module: JWST Transmission Spectroscopy Simulator
Synthesizes atmospheric absorption spectra across infrared wavelengths (0.6 - 12.0 microns).
"""

import numpy as np

def simulate_transmission_spectrum(molecules=None, resolution=100):
    """
    Simulates atmospheric transmission opacity spectrum (transit depth vs wavelength).
    
    Parameters:
        molecules (dict): Relative atmospheric gas fractions (e.g. {'H2O': 0.05, 'CO2': 0.01, 'CH4': 0.005})
        resolution (int): Number of wavelength sampling points
    
    Returns:
        dict: Wavelength array (microns), absorption flux depth (ppm), molecular peak labels
    """
    if not molecules:
        molecules = {'H2O': 0.02, 'CO2': 0.01, 'CH4': 0.005, 'O3': 0.001}
    
    # Wavelength axis from 0.6 to 12.0 microns (JWST NIRSpec + MIRI range)
    wavelengths = np.linspace(0.6, 12.0, resolution)
    
    # Baseline continuum transit depth (1000 ppm)
    baseline_ppm = 1000.0
    transit_depth_ppm = np.full_like(wavelengths, baseline_ppm)
    
    peaks = []
    
    # H2O absorption bands at 1.4µm, 1.9µm, 2.7µm, 6.0µm
    if 'H2O' in molecules and molecules['H2O'] > 0:
        h2o_conc = molecules['H2O']
        band_depth = 250.0 * (h2o_conc / 0.02)
        for center in [1.4, 1.9, 2.7, 6.0]:
            transit_depth_ppm += band_depth * np.exp(-((wavelengths - center) ** 2) / (2 * 0.15 ** 2))
            peaks.append({'molecule': 'H2O', 'wavelength_um': center, 'depth_ppm': round(baseline_ppm + band_depth, 1)})
            
    # CO2 absorption band at 4.3µm and 15µm (edge)
    if 'CO2' in molecules and molecules['CO2'] > 0:
        co2_conc = molecules['CO2']
        band_depth = 320.0 * (co2_conc / 0.01)
        transit_depth_ppm += band_depth * np.exp(-((wavelengths - 4.3) ** 2) / (2 * 0.20 ** 2))
        peaks.append({'molecule': 'CO2', 'wavelength_um': 4.3, 'depth_ppm': round(baseline_ppm + band_depth, 1)})
        
    # CH4 absorption band at 2.3µm, 3.3µm, 7.7µm
    if 'CH4' in molecules and molecules['CH4'] > 0:
        ch4_conc = molecules['CH4']
        band_depth = 180.0 * (ch4_conc / 0.005)
        for center in [2.3, 3.3, 7.7]:
            transit_depth_ppm += band_depth * np.exp(-((wavelengths - center) ** 2) / (2 * 0.18 ** 2))
            peaks.append({'molecule': 'CH4', 'wavelength_um': center, 'depth_ppm': round(baseline_ppm + band_depth, 1)})

    # O3 Ozone absorption band at 9.6µm (key biosignature)
    if 'O3' in molecules and molecules['O3'] > 0:
        o3_conc = molecules['O3']
        band_depth = 210.0 * (o3_conc / 0.001)
        transit_depth_ppm += band_depth * np.exp(-((wavelengths - 9.6) ** 2) / (2 * 0.25 ** 2))
        peaks.append({'molecule': 'O3 (Biosignature)', 'wavelength_um': 9.6, 'depth_ppm': round(baseline_ppm + band_depth, 1)})

    # Add Gaussian instrument noise
    np.random.seed(42)
    noise = np.random.normal(0, 15.0, size=resolution)
    measured_ppm = transit_depth_ppm + noise

    return {
        'status': 'Success',
        'wavelengths_microns': [round(w, 2) for w in wavelengths.tolist()],
        'model_spectrum_ppm': [round(d, 1) for d in transit_depth_ppm.tolist()],
        'measured_spectrum_ppm': [round(d, 1) for d in measured_ppm.tolist()],
        'detected_peaks': peaks,
        'spectral_resolution_R': 300,
        'instrument_model': 'JWST NIRSpec / MIRI Synthetic'
    }
