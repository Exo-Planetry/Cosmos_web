"""
COSMOS ML Module: Candidate False-Positive Classifier (Model B)
Classifies signal candidates into 7 detailed diagnostic categories:
1. Planet Transit Candidate
2. Eclipsing Binary (Stellar Eclipse)
3. Stellar Variability (Rotational Modulation / Spots)
4. Stellar Flare (Magnetic Outburst)
5. Instrument Artifact (CCD Glitch / Thermal Drift)
6. Photometric Noise
7. Uncertain / Undetermined
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List

CATEGORIES = [
    'Planet Transit Candidate',
    'Eclipsing Binary',
    'Stellar Variability',
    'Stellar Flare',
    'Instrument Artifact',
    'Photometric Noise',
    'Uncertain'
]

class FalsePositiveClassifier:
    """Multi-class False Positive Classifier Service."""

    def __init__(self, model_path: str = 'models/false_positive_model.joblib'):
        self.model_path = model_path
        self.model = None
        self.categories = CATEGORIES
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                artifact = joblib.load(self.model_path)
                self.model = artifact['classifier']
                self.categories = artifact.get('categories', CATEGORIES)
                print(f"[FALSE POSITIVE MODEL] Loaded model artifact from {self.model_path}")
            except Exception as e:
                print(f"[FALSE POSITIVE MODEL WARNING] Failed to load artifact: {e}")
                self.model = None

    def classify(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifies candidate signal features into false positive diagnostic categories.
        """
        trandep = float(features.get('pl_trandep', 0.005))
        trandur = float(features.get('pl_trandur', 2.5))
        orbper = float(features.get('pl_orbper', 10.0))
        rade = float(features.get('pl_rade', 1.0))
        imppar = float(features.get('pl_imppar', 0.1))

        if self.model is not None:
            df = pd.DataFrame([features])
            try:
                probs = self.model.predict_proba(df)[0]
                best_idx = np.argmax(probs)
                primary_label = self.categories[best_idx]
                prob_dict = {cat: round(float(p * 100), 1) for cat, p in zip(self.categories, probs)}
            except Exception:
                primary_label = 'Planet Transit Candidate'
                prob_dict = {cat: 14.3 for cat in self.categories}
        else:
            # Physical rule diagnostic classifier fallback
            if trandep > 0.05 or rade > 25.0:
                primary_label = 'Eclipsing Binary'
                fp_risk = 85.0
            elif imppar > 0.9 and trandur < 0.5:
                primary_label = 'Instrument Artifact'
                fp_risk = 75.0
            elif trandep < 0.00005:
                primary_label = 'Photometric Noise'
                fp_risk = 65.0
            elif 0.5 <= rade <= 15.0 and trandep > 0.0001:
                primary_label = 'Planet Transit Candidate'
                fp_risk = 12.0
            else:
                primary_label = 'Uncertain'
                fp_risk = 45.0

            prob_dict = {
                'Planet Transit Candidate': 100.0 - fp_risk if primary_label == 'Planet Transit Candidate' else 15.0,
                'Eclipsing Binary': fp_risk if primary_label == 'Eclipsing Binary' else 10.0,
                'Stellar Variability': 8.0,
                'Stellar Flare': 4.0,
                'Instrument Artifact': fp_risk if primary_label == 'Instrument Artifact' else 5.0,
                'Photometric Noise': fp_risk if primary_label == 'Photometric Noise' else 8.0,
                'Uncertain': 10.0
            }

        # Calculate overall False-Positive Risk (%)
        planet_prob = prob_dict.get('Planet Transit Candidate', 50.0)
        false_positive_risk_pct = round(100.0 - planet_prob, 1)

        return {
            'status': 'Success',
            'primary_diagnostic': primary_label,
            'false_positive_risk_pct': false_positive_risk_pct,
            'category_probabilities': prob_dict,
            'is_candidate_viable': bool(false_positive_risk_pct < 50.0)
        }
