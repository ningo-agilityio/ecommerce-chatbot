import logging
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, validator, Field
from app.chatbot.agent_executor import run_with_memory
from langchain.callbacks.base import BaseCallbackHandler
from fastapi.responses import StreamingResponse

router = APIRouter()

# Pydantic model for user input
class QueryInput(BaseModel):
    keyword: str = Field(..., description="Keyword or phrases to search...")
    @validator('keyword')
    def keyword(cls, value):
        if len(value) < 3:
            raise ValueError('Keyword must be at least 3 characters long')
        if len(value) > 500:
            raise ValueError('Keyword exceeds 500 characters')
        return value

class StreamApiCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs):
        # Collect each new token
        logging.info(token)
        self.tokens.append(token)

    def token_generator(self):
        # Yield tokens one by one as they are generated
        for token in self.tokens:
            yield token
        self.tokens = []

@router.post("/stream")
def search_in_stream(input: QueryInput):
    stream_handler = StreamApiCallbackHandler()
    run_with_memory(input.keyword, stream_handler)
    return StreamingResponse(stream_handler.token_generator(), media_type="text/plain")

@router.post("/search")
def search(input: QueryInput):
    return run_with_memory(input.keyword, None)['output']

