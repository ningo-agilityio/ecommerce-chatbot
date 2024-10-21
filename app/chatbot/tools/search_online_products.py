import os
from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
import logging
# Set up logging
logging.basicConfig(level=logging.INFO)

# Make it work for Python 2+3 and with Unicode
import json

google_api_key_str = os.environ['GOOGLE_API_KEY']
google_api_key_str = google_api_key_str.replace('\\n', '\n')
google_api_key_str = google_api_key_str.replace('\n', '\\n')

logging.info(type(google_api_key_str))

data_loaded = json.loads(google_api_key_str)
data_loaded['private_key'] = data_loaded['private_key'].replace('\\n', '\n')

# data_loaded = json.loads(json_string)
logging.info(type(data_loaded))
logging.info(data_loaded.keys())
class GoogleShoppingService:
  resources: List = None
  def __init__(self) -> None:
    # Load credentials from the service account JSON file (you'll need to create this from Google Cloud Console)
    
    credentials = service_account.Credentials.from_service_account_info(data_loaded)

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
