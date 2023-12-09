import os
from flask import Flask, flash, render_template, abort, request, redirect, url_for, session
from models import db, User, ForumPost
from dotenv import load_dotenv
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from repositories.src.user_repository import player_repository_singleton

load_dotenv()
app = Flask(__name__)

# DB Connection
app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

app.secret_key = os.getenv('APP_SECRET_KEY', 'potato')

db.init_app(app)
bcrypt = Bcrypt()
bcrypt.init_app(app)

socketio = SocketIO(app)

@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')

@app.get('/signup')
def signup():
    saved_input = {}
    return render_template('signup.html', saved_input=saved_input)

@app.template_filter('filter_by_keyword')
def filter_by_keyword(messages, keyword):
    filtered_messages = []
    for message in messages:
        if keyword in message:
            filtered_messages.append(message)
    return filtered_messages

@app.post('/signup')
def create_account():
    saved_input = {}

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    username = request.form.get('username')
    raw_password = request.form.get('password')

    saved_input['first_name'] = first_name
    saved_input['last_name'] = last_name
    saved_input['email'] = email
    saved_input['username'] = username

    if not first_name or not last_name or not email or not username or not raw_password:
        flash("* This is a required field.")
        return render_template('signup.html', saved_input=saved_input)

    email_exists = User.query.filter_by(email=email).first()
    if email_exists:
        flash("☒ This email already exists. Please login.")
        return render_template('signup.html', saved_input=saved_input)

    username_exists = User.query.filter_by(username=username).first()
    if username_exists:
        flash("☒ Username is taken. Please choose another.")
        return render_template('signup.html', saved_input=saved_input)
    
    hashed_password = bcrypt.generate_password_hash(raw_password, 16).decode()
    new_user = User(first_name, last_name, email, username, hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/')

@app.get('/login')
def login():
    return render_template('login.html')

@app.post('/login')
def login_auth():
    username = request.form.get('username')
    raw_password = request.form.get('password')
    if not username or not raw_password:
        flash("* This is a required field.")
        return render_template('login.html')
    existing_user = User.query.filter_by(username=username).first()
    if not existing_user:
        flash("☒ Invalid username or password. Please try again.")
        return render_template('login.html')
    if not bcrypt.check_password_hash(existing_user.password, raw_password):
        flash("☒ Invalid username or password. Please try again.")
        return render_template('login.html')
    session['username'] = username
    return redirect('/')

@app.post('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.get('/profile/<str:username>')
def profile(username: str):

    return render_template('profile.html')

@app.post('/profile')
def player():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    username = request.form.get('username')
    raw_password = request.form.get('password')

    User.first_name = request.form.get('first_name')
    User.last_name = last_name = request.form.get('last_name')
    User.
    active_user = User.query.filter_by(username=username).first()
    session['username'] = {
        'username': 
        'first_name': 
        'last_name': 
        'profile_pic': 
        'bio_text': 
        'game_tags': 
    }
    return render_template('profile.html')

@app.get('/active_game')
def active_game():
    if 'username' in session:
        return render_template('active_game.html')
    return redirect('login')

@app.get('/create_game')
def create_game():
    if 'username' in session:
        return render_template('create_game.html')
    return redirect('login')

@app.get('/join_game')
def join_game():
    if 'username' in session:
        return render_template('join_game.html')
    return redirect('login')

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

@app.get('/chatsession')
def chat():
    return render_template('chat_session.html', user=session['username'])

@socketio.on('set_active_user')
def set_active_user(user_id):
    session['active_user_id'] = user_id
    socketio.emit('active_user_changed', user_id)

@socketio.on('connected')
def handle_connect(json):
    username = json.get('username')
    user = player_repository_singleton.get_user_by_username(username)
    if user:
        set_active_user(user.user_id)

@socketio.on('message')
def handle_message(json):
    user_id = session.get('active_user_id')
    user = player_repository_singleton.get_user_by_id(user_id)
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