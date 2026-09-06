"""
COSMOS Physics Module: Multi-Dimensional Earth Similarity Index (ESI) & Physical Calculators
Includes 6-component ESI decomposition:
1. Radius (w_r = 0.57)
2. Mass / Density (w_d = 1.07)
3. Escape Velocity (w_e = 0.70)
4. Equilibrium Temperature (w_t = 5.58)
5. Surface Gravity (w_g = 0.16)
6. Stellar Flux (w_s = 0.35)
"""

import numpy as np
from typing import Dict, Any

def calculate_multidimensional_esi(
    pl_rade: float,
    pl_bmasse: float = 1.0,
    pl_eqt: float = 288.0,
    st_flux: float = 1.0,
    pl_orbper: float = 365.25
) -> Dict[str, Any]:
    """
    Calculates 6-component multi-dimensional Earth Similarity Index (ESI).
    Returns individual component similarities and composite score.
    """
    pl_rade = float(np.real(pl_rade))
    pl_bmasse = float(np.real(pl_bmasse))
    pl_eqt = float(np.real(pl_eqt))
    st_flux = float(np.real(st_flux))
    pl_orbper = float(np.real(pl_orbper))

    if pl_rade <= 0:
        return {'composite_esi': 0.0, 'components': {}}

    # Earth reference values
    r_earth = 1.0
    m_earth = 1.0
    rho_earth = 1.0  # Normalized density
    ve_earth = 1.0   # Normalized escape velocity
    t_earth = 288.0
    g_earth = 1.0
    s_earth = 1.0

    # Derived physics parameters
    volume = (4.0 / 3.0) * np.pi * (pl_rade ** 3)
    density = pl_bmasse / volume if volume > 0 else 1.0
    v_escape = np.sqrt(pl_bmasse / pl_rade) if pl_rade > 0 else 1.0
    gravity = pl_bmasse / (pl_rade ** 2) if pl_rade > 0 else 1.0

    # Weight factors (Schulze-Makuch et al., 2011)
    w_r = 0.57
    w_d = 1.07
    w_e = 0.70
    w_t = 5.58
    w_g = 0.16
    w_s = 0.35

    # Component similarity functions: s_i = (1 - |(x - x_0) / (x + x_0)|^w_i
    esi_r = (1.0 - abs((pl_rade - r_earth) / (pl_rade + r_earth))) ** w_r
    esi_d = (1.0 - abs((density - rho_earth) / (density + rho_earth))) ** w_d
    esi_e = (1.0 - abs((v_escape - ve_earth) / (v_escape + ve_earth))) ** w_e
    esi_t = (1.0 - abs((pl_eqt - t_earth) / (pl_eqt + t_earth))) ** w_t if pl_eqt > 0 else 0.5
    esi_g = (1.0 - abs((gravity - g_earth) / (gravity + g_earth))) ** w_g
    esi_s = (1.0 - abs((st_flux - s_earth) / (st_flux + s_earth))) ** w_s if st_flux > 0 else 0.5

    # Geometric mean composite ESI
    composite = (esi_r * esi_d * esi_e * esi_t * esi_g * esi_s) ** (1.0 / 6.0)
    composite_clean = float(np.clip(composite, 0.0, 1.0))

    return {
        'composite_esi': round(composite_clean, 3),
        'components': {
            'radius_similarity': round(float(np.clip(esi_r, 0, 1)), 3),
            'density_similarity': round(float(np.clip(esi_d, 0, 1)), 3),
            'escape_velocity_similarity': round(float(np.clip(esi_e, 0, 1)), 3),
            'temperature_similarity': round(float(np.clip(esi_t, 0, 1)), 3),
            'gravity_similarity': round(float(np.clip(esi_g, 0, 1)), 3),
            'stellar_flux_similarity': round(float(np.clip(esi_s, 0, 1)), 3)
        },
        'derived_metrics': {
            'density_earth_relative': round(float(density), 2),
            'surface_gravity_g': round(float(gravity), 2),
            'escape_velocity_earth_relative': round(float(v_escape), 2)
        }
    }

def calculate_esi(pl_rade: float, pl_eqt: float = 288.0, st_teff: float = 5778.0) -> float:
    """Backward compatible ESI helper."""
    res = calculate_multidimensional_esi(pl_rade=pl_rade, pl_eqt=pl_eqt)
    return res['composite_esi']
