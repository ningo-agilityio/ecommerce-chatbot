import os
from google_shopping_service import GoogleShoppingService

from langchain.tools import tool
import wikipedia
from pydantic import BaseModel, Field

# Init google shopping service
google_shopping_service = GoogleShoppingService()

# Define the input schema
class QuerySchemaInput(BaseModel):
    query: str = Field(..., description="Keyword or phrases to search...")

@tool(args_schema=QuerySchemaInput)
def search_wikipedia(query: str) -> str:
    """Run Wikipedia search and get page summaries."""
    page_titles = wikipedia.search(query)
    summaries = []
    for page_title in page_titles[: 3]:
        try:
            wiki_page =  wikipedia.page(title=page_title, auto_suggest=False)
            summaries.append(f"Page: {page_title}\nSummary: {wiki_page.summary}")
        except (
            self.wiki_client.exceptions.PageError,
            self.wiki_client.exceptions.DisambiguationError,
        ):
            pass
    if not summaries:
        return "No good Wikipedia Search Result was found"
    return "\n\n".join(summaries)

@tool(args_schema=QuerySchemaInput)
def search_online_products(query: str) -> str:
    """Fetch current products list rely on provider keywords."""
    responses = []
    try:
        results = google_shopping_service.search(query)
        for record in results:
          responses.append(f"Product name: {record["title"]}\nPrice: {record["price"]["currency"]}{record["price"]["value"]}\nDescription: {record["description"]}")
    except Exception as e:
        print(f"Searching query\n{query}\n raised following error:\n{e}")
    if not responses:
        return "No online product found"
    return "\n\n".join(responses) + "\n"

def create_tools():
  tools = [search_wikipedia, search_online_products]
  return tools
