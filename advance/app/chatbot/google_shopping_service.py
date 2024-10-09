import os
from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
import logging
# Set up logging
logging.basicConfig(level=logging.INFO)
# Example of logging a message
logging.info("This is an info log message")

# Make it work for Python 2+3 and with Unicode
import json
import io
data = json.loads(os.environ['GOOGLE_API_KEY'])
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.abspath(os.path.join(current_dir, 'assets/google_api_key.json'))
# alternative_path = os.path.abspath(os.path.join(current_dir, 'assets/ecommercechatbot-436909-3af585186cb6.json'))
with io.open(file_path, 'w', encoding='utf8') as outfile:
    json.dump(data, outfile)

# Read JSON file
# with open(file_path) as data_file:
#     data_loaded = json.load(data_file)
# logging.info(data_loaded)

class GoogleShoppingService:
  resources: List = None
  def __init__(self) -> None:
    # Load credentials from the service account JSON file (you'll need to create this from Google Cloud Console)
    
    logging.info(file_path)
    credentials = service_account.Credentials.from_service_account_file(file_path)

    # Build the Google Shopping API service
    service = build('content', 'v2.1', credentials=credentials)

    # Make a simple request (e.g., list products from your Merchant account)
    merchant_id = os.environ['GOOGLE_MERCHANT_ID']
    
    self.resources = service.products().list(merchantId=merchant_id).execute()

  def search(self, query):
    products = self.resources.get('resources', [])
    # Filter products based on the search query (you can customize this)
    matching_products = [p for p in products if query.lower() in p['title'].lower()]
    return matching_products
