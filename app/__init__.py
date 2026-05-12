from flask import Flask

app = Flask(__name__)
app.secret_key = 'your-secret-key'
from app import views


