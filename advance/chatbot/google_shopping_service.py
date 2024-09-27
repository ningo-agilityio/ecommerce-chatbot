import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# Load credentials from the service account JSON file (you'll need to create this from Google Cloud Console)
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.abspath(os.path.join(current_dir, os.environ['CLIENT_SECRET_PATH']))
credentials = service_account.Credentials.from_service_account_file(file_path)

# Build the Google Shopping API service
service = build('content', 'v2.1', credentials=credentials)

# Make a simple request (e.g., list products from your Merchant account)
merchant_id = os.environ['GOOGLE_MERCHANT_ID']

response = service.products().list(merchantId=merchant_id).execute()

print(response)