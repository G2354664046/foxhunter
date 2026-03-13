from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import upload, results

app = FastAPI(title="FoxHunter Malware Detection System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(results.router, prefix="/api/v1", tags=["results"])

@app.get("/")
async def root():
    return {"message": "FoxHunter Malware Detection API"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)