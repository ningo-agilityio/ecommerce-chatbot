from fastapi import APIRouter
from pydantic import BaseModel, validator, Field

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
    
@router.post("/stream")
def search_in_stream(input: QueryInput):
    return 'Streaming response'

@router.post("/search")
def search(input: QueryInput):
    return 'Search response'