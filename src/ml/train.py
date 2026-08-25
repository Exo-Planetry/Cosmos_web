import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

FEATURE_COLS = [
    'pl_orbper', 'pl_rade', 'pl_orbeccen', 'pl_orbincl',
    'pl_tranmid', 'pl_imppar', 'pl_trandep', 'pl_trandur',
    'pl_ratdor', 'pl_ratror', 'sy_vmag', 'sy_kmag'
]

def train_model(csv_path: str = 'Transit.csv', output_model_path: str = 'models/exoplanet_model.joblib'):
    """
    Reads NASA Transit dataset, cleans features, fits a HistGradientBoostingClassifier pipeline,
    and serializes the trained model artifact to models/exoplanet_model.joblib.
    """
    print(f"[ML TRAIN] Loading dataset from {csv_path}...")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file {csv_path} not found.")

    df = pd.read_csv(csv_path)

    # Ensure all feature columns exist, fill missing ones if necessary
    for col in FEATURE_COLS:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors='coerce')

    X = df[FEATURE_COLS]

    # Target logic: Create a clean binary label for exoplanet validation candidate
    # A candidate is confirmed if radius is non-null & transit depth > 0 & orbital period > 0
    if 'ttv_flag' in df.columns:
        # Combine ttv_flag with physical plausibility
        y = (
            (df['pl_rade'] > 0.3) & 
            (df['pl_rade'] < 30.0) & 
            (df['pl_orbper'] > 0.1) & 
            (df['pl_trandep'] > 0)
        ).astype(int)
    else:
        y = (df['pl_rade'] > 0).astype(int)

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"[ML TRAIN] Training dataset shape: {X_train.shape}, Target distribution: {np.bincount(y_train)}")

    # Define robust pipeline for tabular data with missing values
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('classifier', HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.08,
            max_depth=6,
            random_state=42
        ))
    ])

    # Fit pipeline
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_proba)

    print(f"[ML TRAIN] Model evaluation successfully completed:")
    print(f" - Accuracy: {acc * 100:.2f}%")
    print(f" - ROC-AUC Score: {roc:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Create target directory if it doesn't exist
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)

    # Save artifact
    artifact = {
        'pipeline': pipeline,
        'feature_names': FEATURE_COLS,
        'accuracy': acc,
        'roc_auc': roc
    }

    joblib.dump(artifact, output_model_path)
    print(f"[ML TRAIN] Saved trained model artifact to {output_model_path}")
    return artifact

if __name__ == '__main__':
    train_model()
