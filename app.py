import os
from flask import Flask, render_template, request, redirect, url_for
from models import *
from dotenv import load_dotenv
from flask_socketio import SocketIO

load_dotenv()
app = Flask(__name__)

# DB Connection
app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

db.init_app(app)

socketio = SocketIO(app)

active_user_id = None

@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')

@app.get('/create_account')
def create_account():
    return render_template('create_account.html')

@app.route('/forum', methods=('GET', 'POST'))
def forum():
    posts = ForumPost.query.order_by(ForumPost.time_posted.desc()).all()
    # display all posts in most-recent first order
    return render_template('forum.html', posts=posts)

@app.get('/forum/<int:post_id>')
def get_single_post(post_id: int):
    return render_template('get_single_post.html')

@app.post('/submit_forum_reply')
def submit_forum_reply():
    # after post, redirect back to get_single_post.html
    return render_template('forum.html')

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author_name = request.form.get('author_name')
        # Will eventually change author_name to author_id once we have login auth setup!
        post = ForumPost(title=title, content=content, author_name=author_name, parent_post_id=None)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('forum'))  # redirect back to GuildBoard main page
    return render_template('create_post.html')

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