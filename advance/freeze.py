from flask_frozen import Freezer
from flask import Flask
app = Flask(__name__)
@app.get("/")
def read_root():
    return "Welcome to the API"

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()