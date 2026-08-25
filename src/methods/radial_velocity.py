import numpy as np
from scipy.optimize import curve_fit
from typing import List, Dict, Any

def sinusoidal(time, A, P, phi, gamma):
    return A * np.sin(2 * np.pi * time / P + phi) + gamma

def analyze_radial_velocity(signal_values: List[float]) -> Dict[str, Any]:
    """
    Fits sinusoidal Keplerian orbit parameters to radial velocity time-series data
    and returns analytical fit metrics for web rendering.
    """
    if len(signal_values) < 4:
        raise ValueError("At least 4 signal values are required for radial velocity curve fitting.")

    time_range = np.linspace(0, len(signal_values) - 1, len(signal_values))
    signal_arr = np.array(signal_values, dtype=float)

    # Initial parameter guess [Amplitude, Period, Phase, Offset]
    initial_guess = [np.std(signal_arr) * np.sqrt(2), len(signal_values) / 2.0, 0.0, np.mean(signal_arr)]

    try:
        popt, _ = curve_fit(sinusoidal, time_range, signal_arr, p0=initial_guess, maxfev=5000)
        amplitude, period, phase, offset = popt
    except Exception:
        amplitude = float(np.ptp(signal_arr) / 2.0)
        period = float(len(signal_values))
        phase = 0.0
        offset = float(np.mean(signal_arr))

    # Confirmation criteria
    is_confirmed = bool(abs(amplitude) > 2.0 and period > 0.5)

    # Generate fine fitted curve points for Plotly rendering
    fit_time = np.linspace(0, len(signal_values) - 1, 100).tolist()
    fit_velocity = sinusoidal(np.array(fit_time), amplitude, period, phase, offset).tolist()

    return {
        'status': 'Success',
        'is_confirmed': is_confirmed,
        'estimated_parameters': {
            'amplitude_ms': round(float(amplitude), 3),
            'orbital_period_days': round(float(abs(period)), 3),
            'phase_rad': round(float(phase), 3),
            'velocity_offset_ms': round(float(offset), 3)
        },
        'raw_time': time_range.tolist(),
        'raw_velocity': signal_arr.tolist(),
        'fit_time': fit_time,
        'fit_velocity': fit_velocity
    }
