"""
COSMOS Astrophysics Module: Kasting & Kopparapu Climate Habitable Zone Model
Evaluates planet position within stellar radiative habitable zone (HZ) boundaries.
Clarifies that HZ position is necessary but NOT sufficient to establish surface habitability.
"""

import numpy as np
from src.utils.physics import calculate_multidimensional_esi

def calculate_habitable_zone(
    stellar_effective_temp: float = 5778.0,
    stellar_luminosity: float = 1.0,
    planet_distance_au: float = 1.0,
    planet_radius_earth: float = 1.0,
    planet_mass_earth: float = 1.0
):
    """
    Calculates Kasting-Kopparapu (2014) HZ boundaries (Recent Venus, Runaway Greenhouse, Maximum Greenhouse, Early Mars).
    Determines Habitable Zone Position and evaluates surface habitability context factors.
    """
    t_diff = stellar_effective_temp - 5778.0

    # Kopparapu et al. (2014) Seff coefficients
    seff_recent_venus = 1.776 + 2.136e-4 * t_diff + 2.533e-8 * (t_diff ** 2)
    seff_runaway_greenhouse = 1.0385 + 1.2456e-4 * t_diff + 1.4612e-8 * (t_diff ** 2)
    seff_max_greenhouse = 0.3507 + 5.9578e-5 * t_diff + 1.6707e-9 * (t_diff ** 2)
    seff_early_mars = 0.3207 + 5.4471e-5 * t_diff + 1.5275e-9 * (t_diff ** 2)

    # Orbital radii boundaries (AU)
    d_recent_venus = float(np.real((max(1e-6, stellar_luminosity / max(1e-6, seff_recent_venus))) ** 0.5))
    d_runaway_greenhouse = float(np.real((max(1e-6, stellar_luminosity / max(1e-6, seff_runaway_greenhouse))) ** 0.5))
    d_max_greenhouse = float(np.real((max(1e-6, stellar_luminosity / max(1e-6, seff_max_greenhouse))) ** 0.5))
    d_early_mars = float(np.real((max(1e-6, stellar_luminosity / max(1e-6, seff_early_mars))) ** 0.5))

    # Stellar flux received by planet S_eff = L_star / d^2
    planet_flux = float(np.real(stellar_luminosity / (planet_distance_au ** 2))) if planet_distance_au > 0 else 1.0

    # Habitable Zone Position classification
    if d_runaway_greenhouse <= planet_distance_au <= d_max_greenhouse:
        zone_position = "Conservative Habitable Zone"
        position_code = "CONSERVATIVE_HZ"
        zone_explanation = "Receives stellar flux suitable for long-term surface liquid water under Earth-like atmospheric greenhouse conditions."
        zone_color = "#00ffb3"
        in_hz = True
    elif d_recent_venus <= planet_distance_au < d_runaway_greenhouse:
        zone_position = "Optimistic Habitable Zone (Inner Boundary / Warm Edge)"
        position_code = "OPTIMISTIC_INNER"
        zone_explanation = "High insolation flux. Risk of moist or runaway greenhouse ocean evaporation."
        zone_color = "#ffb700"
        in_hz = True
    elif d_max_greenhouse < planet_distance_au <= d_early_mars:
        zone_position = "Optimistic Habitable Zone (Outer Boundary / Cold Edge)"
        position_code = "OPTIMISTIC_OUTER"
        zone_explanation = "Low insolation flux. Requires significant CO2 greenhouse warming to prevent global glaciation."
        zone_color = "#00bfe7"
        in_hz = True
    elif planet_distance_au < d_recent_venus:
        zone_position = "Hot Zone (Inside Inner HZ Boundary)"
        position_code = "HOT_INNER"
        zone_explanation = "Extreme stellar irradiance causes rapid water dissociation and runaway atmospheric loss."
        zone_color = "#ff4d4d"
        in_hz = False
    else:
        zone_position = "Cold Zone (Outside Outer HZ Boundary)"
        position_code = "COLD_OUTER"
        zone_explanation = "Insufficient solar heating; volatile gases freeze, leaving surface ice-covered."
        zone_color = "#9999ff"
        in_hz = False

    # Surface Habitability Context Evaluation
    context_notes = []
    if in_hz:
        context_notes.append("Orbit is within the theoretical liquid water radiative flux zone.")
        if planet_radius_earth > 1.6:
            context_notes.append("Large planet radius (>1.6 R_Earth) indicates a Sub-Neptune gas envelope (lacks solid surface).")
        else:
            context_notes.append("Planetary radius (<1.6 R_Earth) is consistent with a rocky terrestrial surface.")
    else:
        context_notes.append("Planet lies outside stellar radiative habitable zone boundaries.")

    # Multi-dimensional ESI calculation
    esi_details = calculate_multidimensional_esi(
        pl_rade=planet_radius_earth,
        pl_bmasse=planet_mass_earth,
        pl_eqt=288.0 * (planet_flux ** 0.25),
        st_flux=planet_flux
    )

    return {
        'status': 'Success',
        'zone_position': zone_position,
        'position_code': position_code,
        'in_habitable_zone': in_hz,
        'zone_color': zone_color,
        'explanation': zone_explanation,
        'scientific_disclaimer': "Habitable Zone position indicates orbital radiative energy balance only. Surface habitability additionally requires a rocky surface, protective magnetosphere, and stable atmosphere.",
        'stellar_effective_temp_k': stellar_effective_temp,
        'stellar_luminosity_l_sun': stellar_luminosity,
        'planet_distance_au': planet_distance_au,
        'planet_stellar_flux_s_earth': round(planet_flux, 3),
        'boundaries_au': {
            'recent_venus': round(d_recent_venus, 4),
            'runaway_greenhouse': round(d_runaway_greenhouse, 4),
            'max_greenhouse': round(d_max_greenhouse, 4),
            'early_mars': round(d_early_mars, 4)
        },
        'habitability_context': context_notes,
        'multidimensional_esi': esi_details
    }
