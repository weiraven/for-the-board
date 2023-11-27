import os
from flask import Flask, render_template, request, redirect, url_for
from models import *
from dotenv import load_dotenv
from flask_socketio import SocketIO
from repositories.src.user_repository import player_repository_singleton

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
        flairs = request.form.get('flairs', '')
        print("Received flairs:", flairs)
        # Will eventually change author_name to author_id once we have login auth setup!
        post = ForumPost(title=title, content=content, author_name=author_name,flairs=flairs, parent_post_id=None)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('forum'))  # redirect back to GuildBoard main page
    return render_template('create_post.html')

@app.get('/signup')
def signup():
    return render_template('signup.html')

@app.post('/profile')
def new_user():
    return render_template('profile.html')

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
        
@app.get('/search_post')
def search_posts():
    query_flair = request.args.get('query-flair', '')
    query_title = request.args.get('query-title', '')
    
    if query_flair:
        query = ForumPost.query.filter(ForumPost.flairs.ilike(f'%{query_flair}%'))
    if query_title:
        query = ForumPost.query.filter(ForumPost.title.ilike(f'%{query_title}%'))
    
    filtered_posts = query.all()
    return render_template('forum.html', posts=filtered_posts)

if __name__ == '__main__':
    socketio.run(app, debug=True)