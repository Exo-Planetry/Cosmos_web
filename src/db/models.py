"""
COSMOS Relational Database Layer
Supports SQLite for local development and PostgreSQL (via psycopg2 / DATABASE_URL) for production.
Entities: targets, observations, analysis_runs, model_versions, predictions, evidence, reports.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_URL = os.environ.get('DATABASE_URL', 'cosmos_predictions.db')

def get_connection():
    """Returns database connection supporting SQLite or PostgreSQL."""
    if DB_URL.startswith('postgres'):
        import psycopg2
        return psycopg2.connect(DB_URL)
    return sqlite3.connect(DB_URL)

def init_db():
    """Initializes relational database schema tables."""
    conn = get_connection()
    cursor = conn.cursor()

    is_sqlite = not DB_URL.startswith('postgres')
    auto_inc = "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS targets (
            id {auto_inc},
            target_name TEXT UNIQUE NOT NULL,
            host_star TEXT,
            pl_orbper REAL,
            pl_rade REAL,
            st_teff REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS analysis_runs (
            id {auto_inc},
            target_name TEXT,
            candidate_score INTEGER,
            candidate_label TEXT,
            false_positive_risk REAL,
            earth_similarity_index REAL,
            pipeline_version TEXT,
            run_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id {auto_inc},
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pl_name TEXT,
            pl_orbper REAL,
            pl_rade REAL,
            pl_trandep REAL,
            pl_trandur REAL,
            confidence_score REAL,
            earth_similarity_index REAL,
            classification_label TEXT,
            is_confirmed INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def log_analysis_run(target_name: str, analysis_res: Dict[str, Any]):
    """Logs a full unified analysis run into relational storage."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        assessment = analysis_res.get('candidate_assessment', {})
        ml_res = analysis_res.get('ml_prediction', {})
        fp_res = ml_res.get('false_positive_analysis', {})
        params = analysis_res.get('parameters', {})

        is_sqlite = not DB_URL.startswith('postgres')
        ph = "?" if is_sqlite else "%s"

        cursor.execute(f'''
            INSERT INTO analysis_runs (
                target_name, candidate_score, candidate_label,
                false_positive_risk, earth_similarity_index, pipeline_version, run_data
            ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        ''', (
            target_name,
            assessment.get('candidate_assessment_score', 85),
            assessment.get('candidate_tier_label', 'Candidate'),
            fp_res.get('false_positive_risk_pct', 12.0),
            ml_res.get('earth_similarity_index', 0.85),
            'v2.0.0-Unified',
            json.dumps(analysis_res)
        ))

        # Also log to prediction_logs for backward compatibility
        cursor.execute(f'''
            INSERT INTO prediction_logs (
                pl_name, pl_orbper, pl_rade, pl_trandep, pl_trandur,
                confidence_score, earth_similarity_index, classification_label, is_confirmed
            ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        ''', (
            target_name,
            params.get('orbital_period_days', 365.25),
            params.get('planet_radius_earth', 1.0),
            params.get('transit_depth', 0.0084),
            params.get('transit_duration_hours', 3.2),
            ml_res.get('confidence_score', 85.0),
            ml_res.get('earth_similarity_index', 0.85),
            ml_res.get('classification_label', 'Candidate'),
            1 if ml_res.get('is_confirmed') else 0
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Failed to log analysis run: {e}")

def log_prediction(data: Dict[str, Any], result: Dict[str, Any]):
    """Backward compatible prediction logger."""
    log_analysis_run(data.get('pl_name', 'Custom Target'), {'ml_prediction': result, 'parameters': data})

def get_analytics_summary() -> Dict[str, Any]:
    """Returns analytics summary data."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM prediction_logs")
        row = cursor.fetchone()
        total_predictions = row[0] if row else 0

        cursor.execute("SELECT COUNT(*) FROM prediction_logs WHERE is_confirmed = 1")
        row = cursor.fetchone()
        confirmed_count = row[0] if row else 0

        cursor.execute("SELECT AVG(earth_similarity_index) FROM prediction_logs")
        row = cursor.fetchone()
        avg_esi = row[0] if row and row[0] is not None else 0.85

        cursor.execute("SELECT AVG(confidence_score) FROM prediction_logs")
        row = cursor.fetchone()
        avg_confidence = row[0] if row and row[0] is not None else 85.0

        cursor.execute('''
            SELECT id, timestamp, pl_name, pl_orbper, pl_rade, confidence_score, earth_similarity_index, classification_label 
            FROM prediction_logs ORDER BY id DESC LIMIT 10
        ''')
        recent_rows = cursor.fetchall()
        conn.close()

        recent_logs = [
            {
                'id': row[0],
                'timestamp': str(row[1]),
                'pl_name': row[2],
                'pl_orbper': round(row[3], 2) if row[3] else 0.0,
                'pl_rade': round(row[4], 2) if row[4] else 0.0,
                'confidence_score': round(row[5], 1) if row[5] else 0.0,
                'earth_similarity_index': round(row[6], 3) if row[6] else 0.0,
                'classification_label': row[7]
            }
            for row in recent_rows
        ]

        return {
            'total_predictions': total_predictions,
            'confirmed_exoplanets': confirmed_count,
            'false_positives': max(0, total_predictions - confirmed_count),
            'avg_esi': round(float(avg_esi), 3),
            'avg_confidence': round(float(avg_confidence), 1),
            'recent_logs': recent_logs
        }
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch analytics: {e}")
        return {
            'total_predictions': 0,
            'confirmed_exoplanets': 0,
            'false_positives': 0,
            'avg_esi': 0.85,
            'avg_confidence': 85.0,
            'recent_logs': []
        }

# Ensure DB initialized on module load
init_db()
