import os
from flask import Flask, render_template, request, redirect, url_for
from models import db
from dotenv import load_dotenv
from flask_socketio import SocketIO
from flask_socketio import SocketIO

# load_dotenv()
# load_dotenv()
app = Flask(__name__)

# # DB connection
# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
# # DB connection
# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

# db.init_app(app)
socketio = SocketIO(app)

users = {
    1: "Damon Nitsavong",
    2: "Phillip Chang",
    3: "Raven Wei",
    4: "Rachel ?",
    5: "Thomas ?",
    6: "Brandon Hach"
}
active_user_id = 1
# db.init_app(app)
socketio = SocketIO(app)

users = {
    1: "Damon Nitsavong",
    2: "Phillip Chang",
    3: "Raven Wei",
    4: "Rachel ?",
    5: "Thomas ?",
    6: "Brandon Hach"
}
active_user_id = 1

@app.route('/', methods=('GET', 'POST'))
def index():  
    return render_template('index.html')

@app.get('/forum')
def forum():
    return render_template('forum.html')

@app.get('/signup')
def signup():
    return render_template('signup.html')

@app.get('/chatsession')
def chat():
    return render_template('chat_session.html', users=users)

@socketio.on('set_active_user')
def set_active_user(user_id):
    global active_user_id
    active_user_id = user_id
    socketio.emit('active_user_changed', user_id)

@socketio.on('connected')
def handle_connect(json):
    username = json.get('username')
    user_id = None
    for uid, uname in users.items():
        if uname == username:
            user_id = uid
            break
    if user_id:
        set_active_user(user_id)

@socketio.on('message')
def handle_message(json):
    username = users.get(active_user_id)  # Get the username based on active_user_id
    if username:
        socketio.emit('message', {'username': username, 'message': json['message']})


if __name__ == '__main__':
    socketio.run(app, debug=True)