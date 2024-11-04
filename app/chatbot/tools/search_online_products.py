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
    # products = self.resources.get('resources', [])
    # Due to issues from Google Shopping API, I will use mock data here:
    # In a real-world scenario, you'd replace this with actual data from Google Shopping API

    products = [
      {
        "title": "Chocolate Mousse",
        "price": {
          "currency": "USD",
          "value": 5.99,
          "country": "USA"
        },
        "description": "A rich and creamy chocolate mousse with a silky texture, made from premium dark chocolate and fresh cream. Perfectly balanced sweetness for chocolate lovers."
      },
      {
        "title": "Vanilla Bean Mini Cake",
        "price": {
          "currency": "USD",
          "value": 4.50,
          "country": "USA"
        },
        "description": "A delightful mini cake infused with real vanilla bean, layered with light frosting. Moist and tender, this treat is ideal for a small indulgence or special celebration."
      },
      {
        "title": "Mini Cake with Chocolate",
        "price": {
          "currency": "USD",
          "value": 6.50,
          "country": "USA"
        },
        "description": "A decadent mini chocolate cake with layers of moist, rich chocolate sponge and smooth chocolate ganache. Topped with a sprinkle of cocoa powder and chocolate shavings, this treat is perfect for satisfying any chocolate craving in a single, delightful serving."
      }
    ]
    
    # Filter products based on the search query (you can customize this)
    matching_products = [p for p in products if query.lower() in p['title'].lower() or query.lower() in p['description'].lower()]
    
    # Return the matching products
    return matching_products
