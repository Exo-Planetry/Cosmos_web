"""
COSMOS — AI-Assisted Exoplanet Discovery & Scientific Analysis Platform
Unified Application Server exposing production REST API endpoints & dashboard views.
"""

import os
from flask import Flask, render_template, request, jsonify
from pydantic import ValidationError

from src.services.analysis_service import run_unified_analysis
from src.services.nasa_service import get_preset_planet, search_nasa_archive, get_nasa_apod, EXOPLANET_PRESETS
from src.services.report_generator import generate_scientific_dossier
from src.methods.radial_velocity import analyze_radial_velocity
from src.methods.transit import analyze_transit_photometry
from src.methods.direct_imaging import analyze_direct_imaging
from src.methods.bio import analyze_biosignature_composition
from src.methods.spectroscopy import simulate_transmission_spectrum
from src.methods.habitable_zone import calculate_habitable_zone
from src.db.models import log_prediction, get_analytics_summary, log_analysis_run
from src.ml.predictor import ExoplanetPredictor

app = Flask(__name__)

# Initialize Predictor Service singleton
predictor = ExoplanetPredictor(model_path='models/tabular_model.joblib')

@app.route('/')
def home():
    apod_data = get_nasa_apod()
    return render_template('index.html', apod=apod_data)

@app.route('/solar')
def solar():
    return render_template('ss.html')

@app.route('/find/<sec>')
def find(sec):
    return render_template('find.html', section_id=sec)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/explore/<sec>')
def explore(sec):
    return render_template('explore.html', section_id=sec)

@app.route('/dashboard')
def dashboard():
    """Renders prediction analytics dashboard."""
    summary = get_analytics_summary()
    return render_template('dashboard.html', summary=summary)

# ==================== UNIFIED PRODUCTION REST API ====================

@app.route('/api/health', methods=['GET'])
def api_health():
    """Production API Health Check Endpoint."""
    return jsonify({
        'status': 'HEALTHY',
        'service': 'COSMOS Exoplanet Analysis Platform API',
        'version': 'v2.0.0-Production',
        'ml_status': 'ACTIVE'
    }), 200

@app.route('/api/targets', methods=['GET'])
def api_list_targets():
    """Returns catalog of known exoplanet targets."""
    query_str = request.args.get('query', '').strip()
    if query_str:
        res = search_nasa_archive(query_str)
        return jsonify(res), 200 if res.get('status') == 'Success' else 404

    # Return list of preset target keys
    preset_list = [
        {
            'key': k,
            'name': v['pl_name'],
            'radius_earth': v['pl_rade'],
            'period_days': v['pl_orbper'],
            'status': v.get('data_status', 'Observed')
        }
        for k, v in EXOPLANET_PRESETS.items()
    ]
    return jsonify({'status': 'Success', 'targets': preset_list}), 200

@app.route('/api/targets/<target_id>', methods=['GET'])
def api_get_target(target_id):
    """Retrieves metadata for specific target."""
    res = search_nasa_archive(target_id)
    if res.get('status') == 'Success':
        return jsonify(res), 200
    return jsonify(res), 404

@app.route('/api/analysis', methods=['POST'])
def api_run_analysis():
    """
    Central Unified Multimodal Exoplanet Analysis Endpoint.
    Supports target search queries, JSON payload parameters, and FITS/CSV file uploads.
    """
    try:
        data = request.get_json(force=True) if request.is_json else request.form.to_dict()
        target_name = data.get('target_name') or request.args.get('target_name')

        # Handle uploaded CSV / FITS files
        light_curve_input = None
        if 'file' in request.files:
            file_obj = request.files['file']
            if file_obj.filename.endswith('.csv'):
                import pandas as pd
                df_upload = pd.read_csv(file_obj)
                cols = [c.lower() for c in df_upload.columns]
                t_col = [c for c in df_upload.columns if 'time' in c.lower() or 'jd' in c.lower()]
                f_col = [c for c in df_upload.columns if 'flux' in c.lower() or 'mag' in c.lower()]
                if t_col and f_col:
                    light_curve_input = {
                        'time': df_upload[t_col[0]].dropna().tolist(),
                        'flux': df_upload[f_col[0]].dropna().tolist()
                    }

        result = run_unified_analysis(
            target_name=target_name,
            custom_parameters=data,
            light_curve_data=light_curve_input
        )

        if result.get('status') == 'Success':
            log_analysis_run(target_name or 'Custom Target', result)
            return jsonify(result), 200
        elif result.get('status') == 'DATA_UNAVAILABLE':
            return jsonify(result), 404

        return jsonify(result), 400

    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/api/analysis/<target_id>/report', methods=['GET'])
def api_get_analysis_report(target_id):
    """Generates official publication-ready scientific dossier HTML report."""
    html_report = generate_scientific_dossier(target_id)
    return html_report, 200, {'Content-Type': 'text/html; charset=utf-8'}

# ==================== LEGACY & SIMULATION API ENDPOINTS ====================

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            raw_data = request.form.to_dict()
            cleaned_data = {k: float(v) if v.replace('.','',1).isdigit() else v for k, v in raw_data.items()}
            result = predictor.predict(cleaned_data)
            log_prediction(cleaned_data, result)
            return render_template('explore.html', prediction_result=result)
        except Exception as e:
            return render_template('explore.html', error=f"Prediction Error: {str(e)}")

    return render_template('explore.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        payload = request.get_json(force=True) if request.is_json else request.form.to_dict()
        numeric_payload = {k: float(v) if str(v).replace('.','',1).replace('-','',1).isdigit() else v for k, v in payload.items()}
        prediction_res = predictor.predict(numeric_payload)
        log_prediction(numeric_payload, prediction_res)
        return jsonify(prediction_res), 200
    except ValidationError as ve:
        return jsonify({'status': 'Error', 'message': 'Input payload validation failed.', 'errors': ve.errors()}), 400
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/api/nasa/apod', methods=['GET'])
def api_nasa_apod():
    return jsonify(get_nasa_apod()), 200

@app.route('/api/nasa/preset/<preset_key>', methods=['GET'])
def api_nasa_preset(preset_key):
    data = get_preset_planet(preset_key)
    if data:
        return jsonify({'status': 'Success', 'data': data}), 200
    return jsonify({'status': 'DATA_UNAVAILABLE', 'message': f"Preset key '{preset_key}' not found."}), 404

@app.route('/api/nasa/search', methods=['GET'])
def api_nasa_search():
    query_str = request.args.get('query', 'Kepler-22')
    res = search_nasa_archive(query_str)
    return jsonify(res), 200 if res.get('status') == 'Success' else 404

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    return jsonify({'status': 'Success', 'data': get_analytics_summary()}), 200

@app.route('/api/simulate/radial_velocity', methods=['POST'])
def api_simulate_rv():
    try:
        data = request.get_json(force=True) if request.is_json else {}
        signals = data.get('signals', [10.0, 5.0, -8.0, -12.0, -4.0, 7.0, 11.0])
        res = analyze_radial_velocity(signals)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/api/simulate/transit', methods=['POST'])
def api_simulate_transit():
    try:
        data = request.get_json(force=True) if request.is_json else {}
        flux_arr = data.get('light_curve', [1.0, 0.99, 0.98, 0.95, 0.95, 0.98, 1.0])
        res = analyze_transit_photometry(flux_arr)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/api/simulate/direct_imaging', methods=['POST'])
def api_simulate_di():
    try:
        data = request.get_json(force=True) if request.is_json else {}
        intensities = data.get('intensities', [1.0, 1.05, 1.8, 1.1, 0.95])
        res = analyze_direct_imaging(intensities)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/api/simulate/biosignature', methods=['POST'])
def api_simulate_biosignature():
    """Exposes missing Biosignature Assessment API Endpoint referenced by frontend predict.js."""
    try:
        data = request.get_json(force=True) if request.is_json else {}
        comp = data.get('composition', {'Oxygen': 0.21, 'Water': 0.02, 'Nitrogen': 0.75, 'CarbonDioxide': 0.01})
        res = analyze_biosignature_composition(comp)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/api/simulate/spectroscopy', methods=['POST'])
def api_simulate_spectroscopy():
    try:
        data = request.get_json(force=True) if request.is_json else {}
        molecules = data.get('molecules', {'H2O': 0.02, 'CO2': 0.01, 'CH4': 0.005, 'O3': 0.001})
        res = simulate_transmission_spectrum(molecules)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/api/simulate/habitable_zone', methods=['POST'])
def api_simulate_hz():
    try:
        data = request.get_json(force=True) if request.is_json else {}
        teff = float(data.get('st_teff', 5778.0))
        lum = float(data.get('st_lum', 1.0))
        dist = float(data.get('pl_orbsmax', 1.0))
        res = calculate_habitable_zone(stellar_effective_temp=teff, stellar_luminosity=lum, planet_distance_au=dist)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/dossier/<planet_name>')
def dossier_report(planet_name):
    html_report = generate_scientific_dossier(planet_name)
    return html_report

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
