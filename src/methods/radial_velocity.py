"""
COSMOS Astrophysics Module: Keplerian Radial Velocity (RV) Orbit Model
Calculates full 6-parameter Keplerian orbital fit:
- Orbital Period (P)
- Semi-amplitude (K)
- Eccentricity (e)
- Argument of Periastron (omega)
- Periastron Epoch (T0)
- Systemic Velocity (gamma)
Returns observed RV points, Keplerian fit curve, and residuals (O - C).
"""

import numpy as np
from scipy.optimize import curve_fit
from typing import List, Dict, Any, Tuple, Optional

def solve_kepler(M: np.ndarray, e: float, tol: float = 1e-6) -> np.ndarray:
    """
    Solves Kepler's Equation M = E - e*sin(E) for Eccentric Anomaly E using Newton-Raphson.
    """
    E = np.copy(M)
    for _ in range(20):
        f = E - e * np.sin(E) - M
        f_prime = 1.0 - e * np.cos(E)
        delta = f / f_prime
        E -= delta
        if np.all(np.abs(delta) < tol):
            break
    return E

def keplerian_rv_model(t: np.ndarray, P: float, K: float, e: float, omega: float, T0: float, gamma: float) -> np.ndarray:
    """
    Evaluates radial velocity v_rv(t) = K * (cos(v + omega) + e * cos(omega)) + gamma
    """
    e = np.clip(e, 0.0, 0.95)
    P = max(1e-3, abs(P))
    mean_anomaly = 2.0 * np.pi * (t - T0) / P
    ecc_anomaly = solve_kepler(mean_anomaly, e)

    # True anomaly v
    sin_v_half = np.sqrt(1.0 + e) * np.sin(ecc_anomaly / 2.0)
    cos_v_half = np.sqrt(1.0 - e) * np.cos(ecc_anomaly / 2.0)
    true_anomaly = 2.0 * np.arctan2(sin_v_half, cos_v_half)

    rv = K * (np.cos(true_anomaly + omega) + e * np.cos(omega)) + gamma
    return rv

def analyze_radial_velocity(
    signal_values: List[float],
    time_points: Optional[List[float]] = None,
    is_simulation: bool = True
) -> Dict[str, Any]:
    """
    Fits full 6-parameter Keplerian orbit to radial velocity time-series data.
    """
    if len(signal_values) < 4:
        raise ValueError("At least 4 signal values are required for Keplerian radial velocity curve fitting.")

    signal_arr = np.array(signal_values, dtype=float)
    if time_points is None:
        time_arr = np.linspace(0, len(signal_values) - 1, len(signal_values))
    else:
        time_arr = np.array(time_points, dtype=float)

    # Initial parameter estimates [P, K, e, omega, T0, gamma]
    p_init = float(max(1.0, (time_arr[-1] - time_arr[0])))
    k_init = float((np.max(signal_arr) - np.min(signal_arr)) / 2.0)
    e_init = 0.05
    omega_init = 0.0
    t0_init = float(time_arr[0])
    gamma_init = float(np.mean(signal_arr))

    initial_guess = [p_init, k_init, e_init, omega_init, t0_init, gamma_init]
    bounds = (
        [0.1, 0.0, 0.0, -np.pi, time_arr[0] - 100, -1000.0],
        [10000.0, 500.0, 0.95, np.pi, time_arr[-1] + 100, 1000.0]
    )

    try:
        popt, pcov = curve_fit(keplerian_rv_model, time_arr, signal_arr, p0=initial_guess, bounds=bounds, maxfev=10000)
        P, K, e, omega, T0, gamma = popt
        perr = np.sqrt(np.diag(pcov)) if pcov is not None else np.zeros(6)
    except Exception:
        P, K, e, omega, T0, gamma = p_init, k_init, e_init, omega_init, t0_init, gamma_init
        perr = np.zeros(6)

    # Calculate model fit & residuals
    fit_model = keplerian_rv_model(time_arr, P, K, e, omega, T0, gamma)
    residuals = signal_arr - fit_model

    # Generate high-resolution curve for chart rendering
    t_fine = np.linspace(time_arr[0], time_arr[-1], 200)
    rv_fine = keplerian_rv_model(t_fine, P, K, e, omega, T0, gamma)

    # Confirmation & quality criteria
    snr = K / (np.std(residuals) + 1e-6)
    is_confirmed = bool(abs(K) > 1.5 and snr >= 3.0)

    return {
        'status': 'Success',
        'data_source_type': 'Simulation' if is_simulation else 'Observed Data',
        'is_confirmed': is_confirmed,
        'estimated_parameters': {
            'semi_amplitude_m_s': round(float(K), 3),
            'semi_amplitude_err': round(float(perr[1]), 3) if perr[1] > 0 else "Uncertainty not available",
            'orbital_period_days': round(float(P), 3),
            'orbital_period_err': round(float(perr[0]), 3) if perr[0] > 0 else "Uncertainty not available",
            'eccentricity': round(float(e), 3),
            'eccentricity_err': round(float(perr[2]), 3) if perr[2] > 0 else "Uncertainty not available",
            'argument_of_periapsis_rad': round(float(omega), 3),
            'systemic_velocity_m_s': round(float(gamma), 3),
            'signal_to_noise_ratio': round(float(snr), 2)
        },
        'raw_time': time_arr.tolist(),
        'raw_velocity': signal_arr.tolist(),
        'fit_time': t_fine.tolist(),
        'fit_velocity': rv_fine.tolist(),
        'residuals': residuals.tolist()
    }
