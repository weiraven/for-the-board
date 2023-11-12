import os
from flask import Flask, render_template, request, redirect, url_for
from models import db
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# DB connection
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

db.init_app(app)

@app.route('/', methods=('GET', 'POST'))
def index():  
    return render_template('index.html')

@app.get('/forum')
def forum():
    return render_template('forum.html')

@app.get('/createAccount')
def account():
    return render_template('account.html')