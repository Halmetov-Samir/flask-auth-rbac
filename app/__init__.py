from flask import Flask

USERS = []
app = Flask(__name__)
app.secret_key = 'your-secret-key'
from app import views


