import numpy as np

def calculate_esi(pl_rade: float, pl_eqt: float = 288.0, st_teff: float = 5778.0) -> float:
    """
    Calculates the Earth Similarity Index (ESI) based on planetary radius and estimated equilibrium temperature.
    ESI = 1.0 represents an exact Earth twin.
    """
    if pl_rade <= 0:
        return 0.0
    
    # Radius weight component (w_r = 0.57)
    esi_r = (1.0 - abs((pl_rade - 1.0) / (pl_rade + 1.0))) ** 0.57
    
    # Temperature weight component (w_t = 0.57)
    t_earth = 288.0  # Kelvin
    esi_t = (1.0 - abs((pl_eqt - t_earth) / (pl_eqt + t_earth))) ** 0.57 if pl_eqt > 0 else 0.5
    
    esi = (esi_r * esi_t) ** 0.5
    return float(np.clip(esi, 0.0, 1.0))

def generate_transit_light_curve(time_points: np.ndarray, depth: float, duration: float, period: float) -> np.ndarray:
    """
    Generates a normalized astronomical transit light curve with ingress and egress profiles.
    """
    flux = np.ones_like(time_points, dtype=float)
    
    # Phase fold time points
    phase = (time_points % period) / period
    transit_center = 0.5
    half_dur = (duration / period) / 2.0
    
    in_transit = np.abs(phase - transit_center) < half_dur
    flux[in_transit] = 1.0 - depth
    
    # Add small Gaussian noise for realistic photometric precision
    noise = np.random.normal(0, depth * 0.05, size=len(time_points))
    return flux + noise

def generate_radial_velocity_curve(time_points: np.ndarray, amplitude: float, period: float) -> np.ndarray:
    """
    Generates a synthetic Keplerian radial velocity sine curve (m/s).
    """
    velocity = amplitude * np.sin(2 * np.pi * time_points / period)
    noise = np.random.normal(0, amplitude * 0.05, size=len(time_points))
    return velocity + noise
