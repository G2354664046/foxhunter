from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bootstrap import bootstrap_default_admin, ensure_admin_table
from app.database import SessionLocal, engine
from app.models.admin_user import AdminUser
from app.routers import auth, cnn_results, dashboard, samples, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_admin_table(engine, AdminUser)
    db = SessionLocal()
    try:
        bootstrap_default_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(title="FoxHunter Admin API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(samples.router, prefix="/api")
app.include_router(cnn_results.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "foxhunter-admin"}
