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
class GoogleShoppingService:
  resources: List = None
  def __init__(self) -> None:
    # Load credentials from the service account JSON file (you'll need to create this from Google Cloud Console)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(current_dir, "assets/ecommercechatbot-436909-2d9e145a5fa8.json"))
    logging.info(file_path)
    logging.info(os.environ['GOOGLE_MERCHANT_ID'])
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
