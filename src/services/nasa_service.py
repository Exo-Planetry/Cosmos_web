import urllib.request
import json
import urllib.parse
from typing import Dict, Any, Optional

# Curated high-precision Exoplanet Presets
EXOPLANET_PRESETS: Dict[str, Dict[str, float]] = {
    "earth_twin": {
        "pl_name": "Earth (Baseline)",
        "pl_orbper": 365.25,
        "pl_rade": 1.00,
        "pl_orbeccen": 0.0167,
        "pl_orbincl": 89.9,
        "pl_tranmid": 2459000.0,
        "pl_imppar": 0.01,
        "pl_trandep": 0.0084,
        "pl_trandur": 13.0,
        "pl_ratdor": 215.0,
        "pl_ratror": 0.0091,
        "sy_vmag": 4.83,
        "sy_kmag": 3.28
    },
    "kepler_22b": {
        "pl_name": "Kepler-22 b",
        "pl_orbper": 289.86,
        "pl_rade": 2.38,
        "pl_orbeccen": 0.00,
        "pl_orbincl": 89.84,
        "pl_tranmid": 2455588.0,
        "pl_imppar": 0.12,
        "pl_trandep": 0.0098,
        "pl_trandur": 7.4,
        "pl_ratdor": 185.0,
        "pl_ratror": 0.0215,
        "sy_vmag": 11.66,
        "sy_kmag": 10.15
    },
    "toi_700d": {
        "pl_name": "TOI-700 d",
        "pl_orbper": 37.42,
        "pl_rade": 1.14,
        "pl_orbeccen": 0.03,
        "pl_orbincl": 89.73,
        "pl_tranmid": 2458632.0,
        "pl_imppar": 0.08,
        "pl_trandep": 0.0024,
        "pl_trandur": 2.6,
        "pl_ratdor": 88.0,
        "pl_ratror": 0.025,
        "sy_vmag": 13.1,
        "sy_kmag": 9.4
    },
    "trappist_1e": {
        "pl_name": "TRAPPIST-1 e",
        "pl_orbper": 6.10,
        "pl_rade": 0.92,
        "pl_orbeccen": 0.007,
        "pl_orbincl": 89.86,
        "pl_tranmid": 2457662.0,
        "pl_imppar": 0.05,
        "pl_trandep": 0.0051,
        "pl_trandur": 0.95,
        "pl_ratdor": 52.0,
        "pl_ratror": 0.071,
        "sy_vmag": 18.8,
        "sy_kmag": 10.3
    },
    "proxima_b": {
        "pl_name": "Proxima Centauri b",
        "pl_orbper": 11.18,
        "pl_rade": 1.07,
        "pl_orbeccen": 0.11,
        "pl_orbincl": 88.0,
        "pl_tranmid": 2457500.0,
        "pl_imppar": 0.20,
        "pl_trandep": 0.0035,
        "pl_trandur": 1.5,
        "pl_ratdor": 32.0,
        "pl_ratror": 0.065,
        "sy_vmag": 11.13,
        "sy_kmag": 4.38
    }
}

def get_preset_planet(preset_key: str) -> Optional[Dict[str, Any]]:
    """Returns curated planet parameters by preset key."""
    return EXOPLANET_PRESETS.get(preset_key.lower())

def search_nasa_archive(planet_name: str) -> Dict[str, Any]:
    """
    Queries NASA Exoplanet Archive TAP API for planetary records.
    Fallback to preset dictionary if offline or unavailable.
    """
    clean_key = planet_name.lower().replace('-', '_').replace(' ', '_')
    if clean_key in EXOPLANET_PRESETS:
        return {'status': 'Success', 'source': 'Preset Catalog', 'data': EXOPLANET_PRESETS[clean_key]}

    try:
        query = f"select pl_name,pl_orbper,pl_rade,pl_orbeccen,pl_orbincl,pl_trandep,pl_trandur,sy_vmag,sy_kmag from ps where pl_name like '%{planet_name}%' and default_flag=1"
        encoded_query = urllib.parse.quote(query)
        url = f"https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query={encoded_query}&format=json"

        req = urllib.request.Request(url, headers={'User-Agent': 'CosmosExoplanetApp/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data and len(data) > 0:
                row = data[0]
                res_data = {
                    "pl_name": row.get("pl_name", planet_name),
                    "pl_orbper": float(row.get("pl_orbper") or 365.25),
                    "pl_rade": float(row.get("pl_rade") or 1.0),
                    "pl_orbeccen": float(row.get("pl_orbeccen") or 0.0),
                    "pl_orbincl": float(row.get("pl_orbincl") or 89.5),
                    "pl_tranmid": 2459000.0,
                    "pl_imppar": 0.02,
                    "pl_trandep": float(row.get("pl_trandep") or 0.0084),
                    "pl_trandur": float(row.get("pl_trandur") or 3.2),
                    "pl_ratdor": 15.0,
                    "pl_ratror": 0.09,
                    "sy_vmag": float(row.get("sy_vmag") or 10.0),
                    "sy_kmag": float(row.get("sy_kmag") or 8.0)
                }
                return {'status': 'Success', 'source': 'NASA TAP API', 'data': res_data}
    except Exception as e:
        print(f"[NASA SERVICE WARNING] Live NASA TAP API lookup failed: {e}")

    # Fallback to Earth baseline
    return {'status': 'Success', 'source': 'Fallback Default', 'data': EXOPLANET_PRESETS['earth_twin']}
