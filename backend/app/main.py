# # backend/app/main.py
# from fastapi import FastAPI

# app = FastAPI(title="RecruitFlow API", version="0.1.0")

# @app.get("/")
# async def root():
#     return {"message": "RecruitFlow Data Ingestion API is live"}




# # Import routes later
# # from app.api import upload_routes, health_routes
# # app.include_router(upload_routes.router)

# backend/app/main.py
from fastapi import FastAPI
from app.api import upload_routes

app = FastAPI(title="RecruitFlow API", version="0.1.0")

# Include your routes
app.include_router(upload_routes.router)

@app.get("/")
async def root():
    return {"message": "RecruitFlow Data Ingestion API is live"}


