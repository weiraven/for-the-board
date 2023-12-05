import os
from flask import Flask, flash, render_template, abort, request, redirect, url_for, session, jsonify
from models import db, User, ForumPost
from dotenv import load_dotenv
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from repositories.src.user_repository import player_repository_singleton
from urllib.parse import urlparse, urljoin

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
    next_url = request.args.get('next')
    return render_template('login.html', next_url=next_url)

@app.post('/login')
def login_auth():
    username = request.form.get('username')
    raw_password = request.form.get('password')
    if not username or not raw_password:
        flash("* This is a required field.")
        return redirect(url_for('login'))
    existing_user = User.query.filter_by(username=username).first()
    if not existing_user:
        flash("☒ Invalid username or password. Please try again.")
        return redirect(url_for('login'))
    if not bcrypt.check_password_hash(existing_user.password, raw_password):
        flash("☒ Invalid username or password. Please try again.")
        return redirect(url_for('login'))
    session['username'] = username
    next_url = request.form.get('next')
    if next_url and is_safe_url(next_url): # check if the next parameter is set and is safe
        return redirect(next_url) # redirect to the next URL
    else:
        return redirect('/') # redirect to home

@app.post('/logout')
def logout():
    session['previous_page'] = request.referrer
    del session['username'] # Log out by removing the session username
    previous_page = session.get('previous_page')
    if previous_page and is_safe_url(previous_page): # Check if the previous page URL is set and is safe
        return redirect(previous_page) # Redirect to the previous page URL
    else:
        return redirect(url_for('login')) # Redirect to the login page

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.get('/profile')
def profile():
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
    for post in posts:
        if not post.category:
            post.category = "None"
        post.category = ''.join(word.capitalize() for word in post.category.split('-'))
    return render_template('forum.html', posts=posts)

@app.get('/forum_post/<int:post_id>')
def get_single_post(post_id):
    post = ForumPost.query.get(post_id)
    if post is None:
        return "Error: Post does not exist" 
    return render_template('get_single_post.html', post=post)

@app.post('/submit_forum_reply')
def submit_forum_reply():
    # after post, redirect back to get_single_post.html
    return render_template('forum.html')

@app.get('/create_post')
def goto_create_post():
    if 'username' in session:
        return render_template('create_post.html')
    else: 
        return redirect(url_for('login', next='/create_post'))

@app.post('/create_post')
def create_post():
    user = User.query.filter_by(username=session['username']).first()
    title = request.form.get('title')
    content = request.form.get('content')
    flairs = request.form.get('flairs', '')
    category = request.form.get('category')
    post = ForumPost(title=title, content=content, author_id=user.user_id, flairs=flairs, parent_post_id=None, category=category)
    db.session.add(post)
    db.session.commit()

    return redirect(url_for('forum'))  # redirect back to GuildBoard main page

@app.get('/edit_post/<int:post_id>')
def edit_post(post_id):
    post = ForumPost.query.get(post_id)
    # check if the session username exists and matches the author of the post
    if 'username' not in session:
        return redirect(url_for('login')) # Redirect to the login page
    if session['username'] == post.author.username:
        return render_template('edit_post.html', post=post)
    else:
        abort(403) # Forbidden

@app.post('/update_post')
def update_post():
    post_id = request.form.get('post_id')
    post = ForumPost.query.get(post_id)
    title = request.form.get('title')
    content = request.form.get('content')
    flairs = request.form.get('flairs', '')
    category = request.form.get('category')

    post.title = title
    post.content = content
    post.flairs = flairs
    post.category = category
    db.session.commit() # commit changes to post
    return redirect(url_for('get_single_post', post_id=post_id))

@app.post('/upvote')
def upvote_post():
    post_id = request.json.get('post_id')
    post = ForumPost.query.get(post_id)
    if post:
        post.upvote()
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Post not found"), 404

@app.post('/downvote')
def downvote_post():
    post_id = request.json.get('post_id')
    post = ForumPost.query.get(post_id)
    if post:
        post.downvote()
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Post not found"), 404

@app.post('/delete_post/<int:post_id>')
def delete_post(post_id):
    # print("delete_post called with post_id:", post_id)  # check if delete posting is working correctly
    post = ForumPost.query.get(post_id)
    if post is None: # if the post does not exist, return a 404
        # print("Post not found")  # error checking
        abort(404)
    if session['username'] != post.author.username: # double check if the current user is the author of the post
        # print("Current user is not the author of the post")  # error checking
        abort(403)

    db.session.delete(post) # remove the post
    db.session.commit()
    # print("Post deleted successfully")  # error checking
    return redirect(url_for('forum')) # redirect back to forum page

@app.post('/profile')
def new_player():
    return render_template('profile.html')

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
    query_category = request.args.get('query-category', '')
    query_flair = request.args.get('query-flair', '')
    query_title = request.args.get('query-title', '')
    subforum = False
    
    query = ForumPost.query
    
    if query_category:
        query = query.filter(ForumPost.category == query_category)
        subforum = True
    
    if query_flair:
        query = query.filter((ForumPost.flairs.ilike(f'%{query_flair}%')))

    if query_title:
        query = query.filter((ForumPost.title.ilike(f'%{query_title}%')))

    filtered_posts = query.all()
    
    if subforum == True:
       return render_template('subforum.html', category=query_category, posts=filtered_posts)

    return render_template('forum.html', posts=filtered_posts)

@app.get('/forum/<category>')
def subforum(category):
    posts = ForumPost.query.filter(ForumPost.category.ilike(f'%{category}%')).all()
    category = ''.join(word.capitalize() for word in category.split('-'))
    
    for post in posts:
        post.category = ''.join(word.capitalize() for word in post.category.split('-'))
        
    return render_template('subforum.html', category = category, posts=posts)

if __name__ == '__main__':
    socketio.run(app, debug=True)