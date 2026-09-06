"""
COSMOS Astronomical Signal Processing: Science-Grade Light Curve Pipeline
Includes Quality Filtering, Sigma Clipping Outlier Removal, Flux Normalization,
Detrending, Box Least Squares (BLS) Period Searching, and Phase Folding.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

def preprocess_light_curve(
    time: np.ndarray,
    flux: np.ndarray,
    sigma_clip: float = 3.5,
    window_size: int = 21
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Cleans raw photometric light curve:
    1. Removes NaNs and invalid flux values.
    2. Normalizes flux to median.
    3. Detrends background trends using moving median filter.
    4. Outlier removal using iterative sigma clipping.
    """
    # 1. Clean NaNs
    valid = np.isfinite(time) & np.isfinite(flux) & (flux > 0)
    time_clean = time[valid]
    flux_raw = flux[valid]

    if len(time_clean) < 10:
        raise ValueError("Insufficient valid photometric data points for light curve processing.")

    # 2. Normalization
    median_flux = float(np.median(flux_raw))
    flux_norm = flux_raw / median_flux

    # 3. Detrending (Moving Median Filter)
    kernel_half = window_size // 2
    flux_trend = np.zeros_like(flux_norm)
    n_pts = len(flux_norm)
    for i in range(n_pts):
        start_idx = max(0, i - kernel_half)
        end_idx = min(n_pts, i + kernel_half + 1)
        flux_trend[i] = np.median(flux_norm[start_idx:end_idx])

    flux_detrended = flux_norm / (flux_trend + 1e-12)

    # 4. Outlier Removal via Sigma Clipping
    std_dev = np.std(flux_detrended)
    mean_val = np.mean(flux_detrended)
    mask = np.abs(flux_detrended - mean_val) <= (sigma_clip * std_dev)

    time_final = time_clean[mask]
    flux_final = flux_detrended[mask]

    metrics = {
        'total_raw_points': len(time),
        'valid_points': int(np.sum(mask)),
        'outliers_removed': int(len(time) - np.sum(mask)),
        'median_baseline_flux': round(median_flux, 5),
        'photometric_precision_ppm': round(float(std_dev * 1e6), 2)
    }

    return time_final, flux_final, flux_trend[mask], metrics

def perform_bls_period_search(
    time: np.ndarray,
    flux: np.ndarray,
    min_period: float = 0.5,
    max_period: float = 30.0,
    n_periods: int = 1000
) -> Dict[str, Any]:
    """
    Executes Box Least Squares (BLS) periodicity search to identify candidate planetary transit signals.
    Uses Astropy BLS if available, otherwise a high-performance vectorised NumPy BLS algorithm.
    """
    time = np.ascontiguousarray(time)
    flux = np.ascontiguousarray(flux)

    # Try astropy.timeseries.BoxLeastSquares
    try:
        from astropy.timeseries import BoxLeastSquares
        model = BoxLeastSquares(time, flux)
        period_grid = np.linspace(min_period, min(max_period, (time[-1] - time[0]) / 2.0), n_periods)
        duration_grid = np.linspace(0.02, 0.3, 10)
        results = model.power(period_grid, duration_grid)

        best_idx = np.argmax(results.power)
        best_period = float(results.period[best_idx])
        best_transit_time = float(results.transit_time[best_idx])
        best_duration = float(results.duration[best_idx])
        best_depth = float(results.depth[best_idx])
        max_power = float(results.power[best_idx])
    except Exception:
        # High-performance NumPy Fallback BLS algorithm
        periods = np.linspace(min_period, min(max_period, max(1.0, (time[-1] - time[0]) / 2.0)), n_periods)
        powers = np.zeros_like(periods)
        best_depths = np.zeros_like(periods)

        baseline = np.mean(flux)
        dur_fraction = 0.05

        for i, p in enumerate(periods):
            phase = (time % p) / p
            in_transit = np.abs(phase - 0.5) < (dur_fraction / 2.0)
            if np.sum(in_transit) > 2 and np.sum(~in_transit) > 2:
                depth = baseline - np.mean(flux[in_transit])
                power = depth * np.sqrt(np.sum(in_transit))
                powers[i] = max(0.0, power)
                best_depths[i] = max(0.0, depth)

        best_idx = np.argmax(powers)
        best_period = float(periods[best_idx])
        best_transit_time = float(time[0] + best_period / 2.0)
        best_duration = float(best_period * dur_fraction * 24.0)  # hours
        best_depth = float(best_depths[best_idx])
        max_power = float(powers[best_idx])

    # Compute Signal-to-Pink-Noise / SNR
    noise = np.std(flux)
    snr = (best_depth / (noise + 1e-9)) * np.sqrt(len(time)) if noise > 0 else 0.0

    return {
        'best_period_days': round(best_period, 4),
        'transit_epoch_jd': round(best_transit_time, 4),
        'transit_duration_hours': round(best_duration * (24.0 if best_duration < 1.0 else 1.0), 3),
        'transit_depth_fraction': round(best_depth, 6),
        'transit_depth_ppm': round(best_depth * 1e6, 1),
        'bls_power': round(max_power, 4),
        'signal_to_noise_ratio': round(float(snr), 2)
    }

def fold_light_curve(
    time: np.ndarray,
    flux: np.ndarray,
    period: float,
    epoch: float = 0.0
) -> Tuple[np.ndarray, np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Phase-folds light curve around the transit center (phase 0.0 at transit epoch).
    Returns folded phase (-0.5 to +0.5), sorted flux, and binned phase curve.
    """
    phase = ((time - epoch) % period) / period
    phase = np.where(phase > 0.5, phase - 1.0, phase)

    sort_idx = np.argsort(phase)
    phase_sorted = phase[sort_idx]
    flux_sorted = flux[sort_idx]

    # Binned curve for smooth transit visualizer
    bins = np.linspace(-0.5, 0.5, 50)
    bin_centers = (bins[:-1] + bins[1:]) / 2.0
    bin_flux = np.zeros_like(bin_centers)

    for i in range(len(bin_centers)):
        mask = (phase_sorted >= bins[i]) & (phase_sorted < bins[i+1])
        if np.any(mask):
            bin_flux[i] = np.median(flux_sorted[mask])
        else:
            bin_flux[i] = 1.0

    return phase_sorted, flux_sorted, (bin_centers, bin_flux)

def generate_box_transit_fit(
    phase: np.ndarray,
    depth: float,
    duration_phase: float
) -> np.ndarray:
    """
    Generates a analytical transit model curve for comparison with residuals.
    """
    fit_flux = np.ones_like(phase, dtype=float)
    in_transit = np.abs(phase) <= (duration_phase / 2.0)
    fit_flux[in_transit] = 1.0 - depth
    return fit_flux

def process_light_curve_pipeline(
    time_series: List[float],
    flux_series: List[float]
) -> Dict[str, Any]:
    """
    Full End-to-End Photometric Light Curve Analysis Pipeline.
    """
    t_arr = np.array(time_series, dtype=float)
    f_arr = np.array(flux_series, dtype=float)

    # Preprocess
    t_clean, f_clean, f_trend, clean_metrics = preprocess_light_curve(t_arr, f_arr)

    # Period search
    bls_res = perform_bls_period_search(t_clean, f_clean)

    # Phase fold
    period = bls_res['best_period_days']
    epoch = bls_res['transit_epoch_jd']
    phase_sorted, flux_sorted, (bin_phase, bin_flux) = fold_light_curve(t_clean, f_clean, period, epoch)

    # Model fit & residuals
    dur_phase = (bls_res['transit_duration_hours'] / 24.0) / period
    fit_flux = generate_box_transit_fit(phase_sorted, bls_res['transit_depth_fraction'], dur_phase)
    residuals = flux_sorted - fit_flux

    return {
        'status': 'Success',
        'quality_metrics': clean_metrics,
        'bls_results': bls_res,
        'raw_light_curve': {
            'time': t_clean.tolist(),
            'flux': f_clean.tolist()
        },
        'phase_folded_light_curve': {
            'phase': phase_sorted.tolist(),
            'flux': flux_sorted.tolist(),
            'binned_phase': bin_phase.tolist(),
            'binned_flux': bin_flux.tolist(),
            'fitted_model_flux': fit_flux.tolist(),
            'residuals': residuals.tolist()
        }
    }
