# COSMOS 5.0 Architecture

## Product
Evidence-driven exoplanet analysis platform. Observed/catalogued, derived and simulated values are explicitly separated.

## Runtime
- FastAPI + Uvicorn
- SQLAlchemy 2.x
- SQLite for local development; PostgreSQL via `DATABASE_URL` for production
- httpx for non-blocking NASA/MAST clients
- Astropy for BoxLeastSquares when installed
- NumPy/scikit-learn for scientific baselines
- Three.js for Solar System visualization

## Backend
`app/api/routes.py` exposes authentication, targets, MAST, unified analysis, upload, simulations, CRUD, comparison, saved targets, comments, alerts, analytics and active-learning endpoints.

`app/core` contains configuration, HMAC JWT security, rate limiting and cache.

`app/db` contains the canonical SQLAlchemy schema and repository operations. Observation and ModelRun are actively written by the analysis pipeline instead of being dead tables.

`app/science` contains transit, RV/Keplerian, imaging, microlensing geometry, atmosphere, habitability, planetary physics and similarity modules.

`app/ml` contains catalog-backed anomaly detection, uncertainty, explainability, SHAP adapter, active learning, model registry and optional advanced PyTorch architectures.

## Data flow
Target/search or upload -> preprocessing -> method-specific analysis -> physical consistency -> evidence fusion -> candidate assessment -> provenance -> database/report.

## Security
Password hashes use scrypt. Tokens are signed HMAC JWT-compatible tokens. API routes are rate limited. User-owned resources require a bearer token. HTML report values are escaped. Frontend uses a shared `escapeHtml` helper before injecting server data.

## Advanced research status
CNN+Transformer, spectral autoencoder, multimodal model and physics-informed objective are real model architectures but are marked research until trained/validated on appropriate labeled astronomical datasets. The system never invents their metrics.
