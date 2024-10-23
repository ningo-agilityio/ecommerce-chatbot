import wikipedia
from langchain.tools import tool
from pydantic import BaseModel, Field
import logging
from app.chatbot.tools.search_online_products import GoogleShoppingService
from app.chatbot.tools.search_on_local_assets.main import LookupLocalAssetsService
from app.chatbot.tools.search_sql_data import QueryProductsSQLDataService

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
    """Search Wikipedia for questions unrelated to products, FAQs, order processes, returns, refunds, or shipping. 
    Retrieve up to three page summaries based on the query."""
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
    """Search online products, especially mousse or mini cakes, using the Google API. 
    If no results are found, fallback to SQL data search."""
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
    """Search local assets (from vector store) for FAQs, order processes, returns, refunds, or shipping information. 
    Sources: faqs.txt, order-process.json, returns-and-refunds.csv, shipping-info.txt."""
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
    """Search the SQL database for product details (title, description, price). 
    If no result is found, fallback to online product search."""
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
