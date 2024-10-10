import os
from fastapi import FastAPI
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
import logging
_ = load_dotenv(find_dotenv())

# Set up logging
logging.basicConfig(level=logging.INFO)
logging.info(os.environ['ALLOW_CORS_ADDRESSES'].split(','))
allow_cors_addresses = os.environ['ALLOW_CORS_ADDRESSES'].split(',')
allow_cors_addresses.append("http://localhost:3000")
app = FastAPI()

# Register API routes
app.include_router(api_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_cors_addresses,  # Or use ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

@app.get("/test")
def read_root():
    return {"message": "Test API"}
