from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .database import init_db
from .routers import auth, results, samples, upload, urlscan, hashscan


app = FastAPI(title="FoxHunter Malware Detection System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    # create tables if they don't exist
    init_db()


# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(results.router, prefix="/api/v1", tags=["results"])
app.include_router(samples.router, prefix="/api/v1", tags=["samples"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(urlscan.router, prefix="/api/v1", tags=["url"])
app.include_router(hashscan.router, prefix="/api/v1", tags=["hash"])

@app.get("/")
async def root():
    return RedirectResponse("http://localhost:5173/")

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)