import wikipedia
from langchain.tools import tool
from pydantic import BaseModel, Field
import logging
from app.chatbot.google_shopping_service import GoogleShoppingService
from app.chatbot.lookup_local_assets_service import LookupLocalAssetsService
from app.chatbot.query_products_sql_data_service import QueryProductsSQLDataService

from wikipedia.exceptions import PageError, DisambiguationError

# Init google shopping service
google_shopping_service = GoogleShoppingService()
local_assets_service = LookupLocalAssetsService()
query_products_sql_data_service = QueryProductsSQLDataService()

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
        except (PageError, DisambiguationError) as e:
            logging.error(f"Searching query fail for input: {query}. Error: {e}")
            pass
            return ""  # Return None or a specific message
        except Exception as e:
            logging.error(f"Searching query fail for input: {query}. Error: {e}")
            raise
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
          responses.append(f"Product name: {record['title']}\nPrice: {record['price']['currency']}{record['price']['value']}\nDescription: {record['description']}")
    except Exception as e:
        logging.error(f"Searching query fail for input: {query}. Error: {e}")
        raise
    if not responses:
        return "No online product found"
    return "\n\n".join(responses) + "\n"

@tool(args_schema=QuerySchemaInput)
def search_on_local_assets(query: str) -> str:
    """Search keyword on local assets faqs.txt and data in Sqlite"""
    result = ''
    try:
        response = local_assets_service.search(query)
        logging.info(response)
        if isinstance(response, dict) and "input" in response:
            result = response['text']
        else:
            result = response
    except Exception as e:
        logging.error(f"Searching query fail for input: {query}. Error: {e}")
        raise
    if not result:
        return "No result found correspond to given keyword"
    return result + "\n"

@tool(args_schema=QuerySchemaInput)
def search_sql_data(query: str) -> str:
    """Search keyword on sql data"""
    result = ''
    try:
        response = query_products_sql_data_service.search(query)
        logging.info(response)
        if isinstance(response, dict) and "input" in response:
            result = response['output']
        else:
            result = response
    except Exception as e:
        logging.error(f"Searching query fail for input: {query}. Error: {e}")
        raise
    if not result:
        return "No result found correspond to given keyword"
    return result + "\n"

def create_tools():
  tools = [search_wikipedia, search_sql_data, search_online_products, search_on_local_assets]
  return tools
