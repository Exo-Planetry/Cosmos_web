import os
from flask import Flask, render_template, request, jsonify
from pydantic import ValidationError

from src.ml.predictor import ExoplanetPredictor
from src.methods.radial_velocity import analyze_radial_velocity
from src.methods.transit import analyze_transit_photometry
from src.methods.direct_imaging import analyze_direct_imaging
from src.methods.bio import analyze_biosignature_composition
from src.db.models import log_prediction, get_analytics_summary
from src.services.nasa_service import get_preset_planet, search_nasa_archive

app = Flask(__name__)

# Initialize Predictor Service singleton
predictor = ExoplanetPredictor(model_path='models/exoplanet_model.joblib')

@app.route('/')
def home():
    return render_template('index.html')

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
    """Renders the prediction analytics dashboard page."""
    summary = get_analytics_summary()
    return render_template('dashboard.html', summary=summary)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Traditional HTML form submission route."""
    if request.method == 'POST':
        try:
            raw_data = request.form.to_dict()
            cleaned_data = {}
            for k, v in raw_data.items():
                try:
                    cleaned_data[k] = float(v)
                except (ValueError, TypeError):
                    cleaned_data[k] = v

            result = predictor.predict(cleaned_data)
            log_prediction(cleaned_data, result)
            return render_template('explore.html', prediction_result=result)
        except Exception as e:
            return render_template('explore.html', error=f"Prediction Error: {str(e)}")

    return render_template('explore.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Production JSON REST API Endpoint for Exoplanet & Habitability Prediction."""
    try:
        payload = request.get_json(force=True) if request.is_json else request.form.to_dict()

        numeric_payload = {}
        for k, v in payload.items():
            try:
                numeric_payload[k] = float(v)
            except (ValueError, TypeError):
                numeric_payload[k] = v

        prediction_res = predictor.predict(numeric_payload)
        
        # Log to Database
        log_prediction(numeric_payload, prediction_res)

        return jsonify(prediction_res), 200

    except ValidationError as ve:
        return jsonify({
            'status': 'Error',
            'message': 'Input payload validation failed.',
            'errors': ve.errors()
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'Error',
            'message': str(e)
        }), 500

@app.route('/api/nasa/preset/<preset_key>', methods=['GET'])
def api_nasa_preset(preset_key):
    """API endpoint to get pre-configured exoplanet preset metrics."""
    data = get_preset_planet(preset_key)
    if data:
        return jsonify({'status': 'Success', 'data': data}), 200
    return jsonify({'status': 'Error', 'message': 'Preset target not found.'}), 404

@app.route('/api/nasa/search', methods=['GET'])
def api_nasa_search():
    """API endpoint to search live NASA Exoplanet Archive."""
    query_str = request.args.get('query', 'Kepler-22')
    res = search_nasa_archive(query_str)
    return jsonify(res), 200

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    """API endpoint returning prediction statistics and history."""
    summary = get_analytics_summary()
    return jsonify({'status': 'Success', 'data': summary}), 200

@app.route('/api/simulate/radial_velocity', methods=['POST'])
def api_simulate_rv():
    """API endpoint for Radial Velocity curve analysis."""
    try:
        data = request.get_json(force=True)
        signals = data.get('signals', [10.0, 5.0, -8.0, -12.0, -4.0, 7.0, 11.0])
        res = analyze_radial_velocity(signals)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/api/simulate/transit', methods=['POST'])
def api_simulate_transit():
    """API endpoint for Transit light curve photometry analysis."""
    try:
        data = request.get_json(force=True)
        flux_arr = data.get('light_curve', [1.0, 0.99, 0.98, 0.95, 0.95, 0.98, 1.0])
        res = analyze_transit_photometry(flux_arr)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/api/simulate/direct_imaging', methods=['POST'])
def api_simulate_di():
    """API endpoint for Direct Imaging spatial signal intensity."""
    try:
        data = request.get_json(force=True)
        intensities = data.get('intensities', [1.0, 1.05, 1.8, 1.1, 0.95])
        res = analyze_direct_imaging(intensities)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

@app.route('/api/simulate/biosignature', methods=['POST'])
def api_simulate_bio():
    """API endpoint for atmospheric chemical biosignature analysis."""
    try:
        data = request.get_json(force=True)
        composition = data.get('composition', {'Oxygen': 0.22, 'Water': 0.02, 'Nitrogen': 0.75})
        res = analyze_biosignature_composition(composition)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
