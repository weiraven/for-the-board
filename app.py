import os
from flask import Flask, render_template, request, redirect, url_for
from models import db
from dotenv import load_dotenv
from flask_socketio import SocketIO
from repositories.src.user_repository import player_repository_singleton

load_dotenv()
app = Flask(__name__)

# DB connection
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

socketio = SocketIO(app)

active_user_id = None

@app.route('/', methods=('GET', 'POST'))
def index():  
    return render_template('index.html')

@app.get('/forum')
def forum():
    return render_template('forum.html')

@app.get('/chatsession')
def chat():
    users = player_repository_singleton.get_all_users()
    return render_template('chat_session.html', users=users)

@socketio.on('set_active_user')
def set_active_user(user_id):
    global active_user_id
    active_user_id = user_id
    socketio.emit('active_user_changed', user_id)

@socketio.on('connected')
def handle_connect(json):
    username = json.get('username')
    user = player_repository_singleton.get_user_by_username(username)
    if user:
        set_active_user(user.user_id)

@socketio.on('message')
def handle_message(json):
    user = player_repository_singleton.get_user_by_id(active_user_id)
    if user:
        socketio.emit('message', {'username': user.username, 'message': json['message']})

if __name__ == '__main__':
    socketio.run(app, debug=True)