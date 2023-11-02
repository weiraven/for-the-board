from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def index():  
    return render_template('index.html')

@app.get('/forum')
def forum():
    return render_template('forum.html')

@app.get('/createAccount')
def account():
    return render_template('account.html')