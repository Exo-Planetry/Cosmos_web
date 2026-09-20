from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.core.config import CORS_ORIGINS, APP_VERSION
from app.db.database import init_db
from app.db.seed import seed_reference

BASE_DIR = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(app):
    init_db()
    try: 
        seed_reference()
    except Exception: 
        pass
    yield

app = FastAPI(
    title='COSMOS',
    version=APP_VERSION,
    description='Scientific exoplanet research platform',
    lifespan=lifespan,
    docs_url='/docs',
    redoc_url='/redoc'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['GET','POST','PUT','DELETE'],
    allow_headers=['*']
)

app.include_router(router)

# Serve the static built files from React
frontend_dist = BASE_DIR / 'frontend' / 'dist'
if frontend_dist.exists():
    app.mount('/assets', StaticFiles(directory=str(frontend_dist / 'assets')), name='assets')

    @app.api_route("/{path_name:path}", methods=["GET"])
    async def catch_all(request: Request, path_name: str):
        # Ignore API routes
        if path_name.startswith("api/"):
            return None
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Frontend not built. Run npm run build in frontend directory."}
