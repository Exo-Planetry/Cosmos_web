# COSMOS 5.0

COSMOS is a responsive exoplanet research workspace combining NASA/MAST target discovery, scientific analysis modules, candidate assessment, provenance, comparison and a Solar System simulator.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` and `/docs` for Swagger.

## Production
Set `DATABASE_URL` and `COSMOS_SECRET` on Render. The included `render.yaml` uses Uvicorn. Never use the development secret in production.

## Scientific integrity
The candidate score is an evidence summary, not a planet confirmation. Simulations are marked simulated; catalog values are catalogued; physics outputs are derived. Advanced ML architectures are not presented as trained models until a reproducible training/validation dataset exists.
