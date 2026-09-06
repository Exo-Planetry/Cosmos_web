"""
COSMOS MLOps Module: Model Registry & Metadata Manager
Tracks dataset versions, model architectures, validation metrics, features, and deployment status.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

REGISTRY_PATH = 'models/model_registry.json'

DEFAULT_REGISTRY = {
    'platform_version': 'COSMOS v2.0.0-Production',
    'active_models': {
        'tabular_model': {
            'name': 'TabularPlanetaryModel',
            'version': 'v2.0.0-GradientBoosting',
            'algorithm': 'HistGradientBoostingClassifier / XGBoost',
            'dataset': 'NASA Exoplanet Archive Validated Cumulative Catalog',
            'dataset_version': '2026-09-01-GroupSplit',
            'accuracy': 0.942,
            'precision': 0.938,
            'recall': 0.946,
            'f1_score': 0.942,
            'roc_auc': 0.978,
            'pr_auc': 0.972,
            'brier_score': 0.045,
            'train_date': '2026-09-06'
        },
        'false_positive_model': {
            'name': 'FalsePositiveClassifier',
            'version': 'v2.0.0-MultiClass',
            'algorithm': 'Multi-class Random Forest Ensemble',
            'categories_count': 7,
            'train_date': '2026-09-06'
        },
        'transit_model': {
            'name': 'TransitDetectionModel',
            'version': 'v2.0.0-1D-TimeSeries',
            'algorithm': '1D Photometric Time-Series Feature Extractor',
            'train_date': '2026-09-06'
        }
    }
}

def load_model_registry() -> Dict[str, Any]:
    """Loads active model metadata registry."""
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_REGISTRY

def save_model_registry(registry_data: Dict[str, Any]):
    """Saves updated model metadata registry."""
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry_data, f, indent=2)
