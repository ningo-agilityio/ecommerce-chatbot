from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI()

# Register API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

@app.get("/test")
def read_root():
    return {"message": "Test API"}
