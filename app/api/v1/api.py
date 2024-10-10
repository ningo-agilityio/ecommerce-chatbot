from fastapi import APIRouter
from app.api.v1.chatbot import router

# Create a new APIRouter instance
api_router = APIRouter()

# Include individual routers from endpoints
# This binds the chatbot endpoints under `/chatbot` routes, respectively.
api_router.include_router(router, prefix="/chatbot", tags=["chatbot"])
