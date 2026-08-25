"""
COSMOS Astrophysics Module: Kasting & Kopparapu Climate Habitable Zone Model
Calculates stellar flux thresholds (Seff) and habitable zone radii (AU) for host stars.
"""

def calculate_habitable_zone(stellar_effective_temp=5778.0, stellar_luminosity=1.0, planet_distance_au=1.0):
    """
    Calculates 4 Kasting-Kopparapu Habitable Zone boundary limits:
    1. Recent Venus (Inner Limit)
    2. Runaway Greenhouse (Conservative Inner Boundary)
    3. Maximum Greenhouse (Conservative Outer Boundary)
    4. Early Mars (Outer Limit)
    
    Parameters:
        stellar_effective_temp (float): Star Effective Temperature in Kelvin (Solar = 5778 K)
        stellar_luminosity (float): Stellar Luminosity in Solar Units (L_sun = 1.0)
        planet_distance_au (float): Semi-major axis distance of planet in AU
    """
    # Normalize stellar temperature difference from solar (T_eff - 5778 K)
    t_diff = stellar_effective_temp - 5778.0

    # Peer-reviewed Kopparapu et al. (2013/2014) polynomial coefficients for Seff
    # Seff = Seff_sun + a*T + b*T^2 + c*T^3 + d*T^4
    seff_recent_venus = 1.776 + 2.136e-4 * t_diff + 2.533e-8 * (t_diff ** 2)
    seff_runaway_greenhouse = 1.0385 + 1.2456e-4 * t_diff + 1.4612e-8 * (t_diff ** 2)
    seff_max_greenhouse = 0.3507 + 5.9578e-5 * t_diff + 1.6707e-9 * (t_diff ** 2)
    seff_early_mars = 0.3207 + 5.4471e-5 * t_diff + 1.5275e-9 * (t_diff ** 2)

    # Convert Seff thresholds to orbital distance radii (d = sqrt(L_star / Seff))
    d_recent_venus = (stellar_luminosity / seff_recent_venus) ** 0.5
    d_runaway_greenhouse = (stellar_luminosity / seff_runaway_greenhouse) ** 0.5
    d_max_greenhouse = (stellar_luminosity / seff_max_greenhouse) ** 0.5
    d_early_mars = (stellar_luminosity / seff_early_mars) ** 0.5

    # Planet stellar flux received (S_planet = L_star / d^2)
    planet_flux = stellar_luminosity / (planet_distance_au ** 2) if planet_distance_au > 0 else 1.0

    # Determine status
    if d_runaway_greenhouse <= planet_distance_au <= d_max_greenhouse:
        zone_status = "Conservative Habitable Zone (Prime Candidate for Liquid Water)"
        is_habitable = True
        zone_color = "#00ffb3"
    elif d_recent_venus <= planet_distance_au < d_runaway_greenhouse:
        zone_status = "Optimistic Habitable Zone (Inner Edge - High Insolation)"
        is_habitable = True
        zone_color = "#ffb700"
    elif d_max_greenhouse < planet_distance_au <= d_early_mars:
        zone_status = "Optimistic Habitable Zone (Outer Edge - Cold Climate)"
        is_habitable = True
        zone_color = "#00bfe7"
    elif planet_distance_au < d_recent_venus:
        zone_status = "Too Hot (Inside Inner Boundary - High Stellar Flux)"
        is_habitable = False
        zone_color = "#ff4d4d"
    else:
        zone_status = "Too Cold (Outside Outer Boundary - Frozen Realm)"
        is_habitable = False
        zone_color = "#9999ff"

    return {
        'status': 'Success',
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
        'zone_classification': zone_status,
        'is_habitable': is_habitable,
        'zone_color': zone_color,
        'model': 'Kasting & Kopparapu (2014) Climate Radiative Transfer'
    }
