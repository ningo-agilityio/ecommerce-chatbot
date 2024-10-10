# from flask import Flask
# from pydantic import BaseModel, validator, Field
# from app.chatbot.agent_executor import run_with_memory
# from app.api.v1.api import api_router

# import logging
# # Set up logging
# logging.basicConfig(level=logging.INFO)

# # app = Flask(__name__)

# fastapi_app = FastAPI()

# # # Register API routes
# fastapi_app.include_router(api_router, prefix="/api/v1")


# Pydantic model for user input
# class QueryInput(BaseModel):
#     keyword: str = Field(..., description="Keyword or phrases to search...")
#     @validator('keyword')
#     def keyword(cls, value):
#         if len(value) < 3:
#             raise ValueError('Keyword must be at least 3 characters long')
#         if len(value) > 500:
#             raise ValueError('Keyword exceeds 500 characters')
#         return value

# @app.get("/")
# def read_root():
#     return "Welcome to the API"

# @app.post("/search")
# def search(input: QueryInput):
#     return run_with_memory(input.keyword, None)['output']

# @app.post("/stream")
# def search_stream(input: QueryInput):
#     return 'Streaming response'

# if __name__ == '__main__':
#     logging.info('Running API')

#     import uvicorn
#     uvicorn.run(fastapi_app)

from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI()

# Register API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
