import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, List

DB_PATH = os.environ.get('DATABASE_URL', 'cosmos_predictions.db')

def init_db():
    """Initializes SQLite database tables for prediction tracking."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

def log_prediction(data: Dict[str, Any], result: Dict[str, Any]):
    """Logs a prediction entry into the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        details = result.get('details', {})
        cursor.execute('''
            INSERT INTO prediction_logs (
                pl_name, pl_orbper, pl_rade, pl_trandep, pl_trandur,
                confidence_score, earth_similarity_index, classification_label, is_confirmed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('pl_name', 'Custom Target'),
            details.get('orbital_period_days', data.get('pl_orbper', 0.0)),
            details.get('planet_radius_earth', data.get('pl_rade', 0.0)),
            details.get('transit_depth', data.get('pl_trandep', 0.0)),
            details.get('transit_duration_hours', data.get('pl_trandur', 0.0)),
            result.get('confidence_score', 0.0),
            result.get('earth_similarity_index', 0.0),
            result.get('classification_label', 'Unknown'),
            1 if result.get('is_confirmed') else 0
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Failed to log prediction: {e}")

def get_analytics_summary() -> Dict[str, Any]:
    """Retrieves aggregated analytics metrics for dashboard rendering."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM prediction_logs")
        total_predictions = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM prediction_logs WHERE is_confirmed = 1")
        confirmed_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT AVG(earth_similarity_index) FROM prediction_logs")
        avg_esi = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(confidence_score) FROM prediction_logs")
        avg_confidence = cursor.fetchone()[0] or 0.0

        cursor.execute('''
            SELECT id, timestamp, pl_name, pl_orbper, pl_rade, confidence_score, earth_similarity_index, classification_label 
            FROM prediction_logs ORDER BY id DESC LIMIT 10
        ''')
        recent_rows = cursor.fetchall()
        conn.close()

        recent_logs = [
            {
                'id': row[0],
                'timestamp': row[1],
                'pl_name': row[2],
                'pl_orbper': round(row[3], 2),
                'pl_rade': round(row[4], 2),
                'confidence_score': round(row[5], 1),
                'earth_similarity_index': round(row[6], 3),
                'classification_label': row[7]
            }
            for row in recent_rows
        ]

        return {
            'total_predictions': total_predictions,
            'confirmed_exoplanets': confirmed_count,
            'false_positives': total_predictions - confirmed_count,
            'avg_esi': round(avg_esi, 3),
            'avg_confidence': round(avg_confidence, 1),
            'recent_logs': recent_logs
        }
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch analytics: {e}")
        return {
            'total_predictions': 0,
            'confirmed_exoplanets': 0,
            'false_positives': 0,
            'avg_esi': 0.0,
            'avg_confidence': 0.0,
            'recent_logs': []
        }

# Ensure DB table exists on module load
init_db()
