import logging
import sqlite3
import os
import json
import csv

# Connect to SQLite (creates a new database file if it doesn't exist)
conn = sqlite3.connect('ecommerce_chatbot.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Example: Create a table to store text data
cursor.execute('''
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    name TEXT,
    content TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    price INTEGER
)
''')
conn.commit()

# Check whether data is existing or not
def check_existing_documents():
    cursor.execute('SELECT * FROM documents')
    result = cursor.fetchone()
    if (result):
        return result
    return False

def check_existing_products():
    cursor.execute('SELECT * FROM products')
    result = cursor.fetchone()
    if (result):
        return result
    return False

def retrieve_documents():
    cursor.execute('SELECT * FROM documents')
    result = cursor.fetchall()
    return result

def get_full_file_path(file_name:str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, '../app/chatbot', file_name))

# Read and save data from order-process.json
def load_order_process():
    with open(get_full_file_path('assets/order-process.json'), 'r') as file:
        data = json.load(file)
    # Insert data into the database
    cursor.execute('INSERT INTO documents (name, content) VALUES (?, ?)', 
        ('order_process', ', '.join([str(x) for x in data['steps']])))
    cursor.execute('INSERT INTO documents (name, content) VALUES (?, ?)', 
        ('order_process', ', '.join([str(x) for x in data['payment_methods']])))

# Read and save data from products-information.txt
def load_products_information():
    with open(get_full_file_path('assets/products-information.txt'), 'r') as file:
        docs = file.readlines()

    # Insert data into the database
    for doc in docs:
        cursor.execute('INSERT INTO documents (name, content) VALUES (?, ?)', 
            ('products_information', doc))

# Read and save data from returns-and-refunds.csv
def load_returns_and_refunds():
    with open(get_full_file_path('assets/returns-and-refunds.csv'), 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            category, return_window, condition = row
            cursor.execute('INSERT INTO documents (name, content) VALUES (?, ?)', 
                ('returns_and_refunds', category + ',' + return_window + ',' + condition))

# Read and save data from shipping-info.txt
def load_shipping_information():
    with open(get_full_file_path('assets/shipping-info.txt'), 'r') as file:
        docs = file.readlines()

    # Insert data into the database
    for doc in docs:
        cursor.execute('INSERT INTO documents (name, content) VALUES (?, ?)', 
            ('shipping_information', doc))

def init_and_retrieve_documents():
    records = check_existing_documents()
    if (records is False):
        load_order_process()
        # Remove to avoid conflict data - get back to to check later 
        # load_products_information()
        load_returns_and_refunds()
        load_shipping_information()
        conn.commit()  # Save changes
    records = retrieve_documents()
    conn.commit()  # Save changes
    return records

def insert_products():
    with open(get_full_file_path('assets/products.json'), 'r') as file:
        products = json.load(file)
        logging.info(products)
        for item in products:
            cursor.execute('INSERT INTO products (title, description, price) VALUES (?, ?, ?)', 
                    (item['title'], item['description'], item['price']))
    
def init_products():
    records = check_existing_products()
    if (records is False):
        insert_products()
        conn.commit()  # Save changes# Save changes
