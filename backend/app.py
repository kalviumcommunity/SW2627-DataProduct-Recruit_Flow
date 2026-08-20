from fastapi import FastAPI
from backend.routes import analytics, candidates, departments, upload

app = FastAPI(title="RecruitFlow Intelligence API", version="1.0.0")

app.include_router(analytics.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(departments.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "RecruitFlow Recruitment Intelligence API is live"}

