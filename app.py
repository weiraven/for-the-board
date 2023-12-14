import os, random, requests, json as jsons
import re
from flask import Flask, flash, render_template, abort, request, redirect, url_for, session, jsonify
from models import db, User, ForumPost, Vote, Game, ActiveGame, GameSession, GameTag, ForumDescription
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_bcrypt import Bcrypt
from repositories.src.user_repository import player_repository_singleton
from repositories.src.game_repository import game_repository_singleton
from urllib.parse import urlparse, urljoin
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/profile_pics'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

load_dotenv()
app = Flask(__name__)

#For local DB connection only:
# app.config[
#     'SQLALCHEMY_DATABASE_URI'
# ] = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = os.getenv('APP_SECRET_KEY', 'potato')

db.init_app(app)
bcrypt = Bcrypt()
bcrypt.init_app(app)

socketio = SocketIO(app, cors_allowed_origins="*")
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    # Log in the new user upon successful account creation
    session['username'] = new_user.username
    session['user_id'] = new_user.user_id
    return redirect('/')

@app.get('/login')
def login():
    next_url = request.args.get('next') or request.referrer
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
    user_id = existing_user.user_id # get logged-in user's user_id
    session['username'] = username # store user's username
    session['user_id'] = user_id # store user's id in session dictionary as well
    session['profile_pic'] = existing_user.profile_pic
    next_url = request.form.get('next')
    if next_url and is_safe_url(next_url): # check if the next parameter is set and is safe
        return redirect(next_url) # redirect to the next URL
    else:
        return redirect('/') # redirect to home

@app.route('/is_logged_in') # if user is in session, send status as json to requester
def is_logged_in():
    return jsonify(is_logged_in='user_id' in session)

@app.post('/logout')
def logout():
    last_visited = session.get('last_visited')
    session.clear()
    if last_visited and is_safe_url(last_visited): # Check if the previous page URL is set and is safe
        return redirect(last_visited) # Redirect to the previous page URL
    else:
        return redirect(url_for('login')) # Redirect to the login page

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.get('/profile/<int:user_id>')
def profile(user_id:int):
    active_user = User.query.filter_by(user_id = user_id).first()
    
    if active_user is None:
        return "Error: User does not exist"
    
    sessionUser = ''
    if session.__contains__('username') and session['username']:
        sessionUser = session['username']

    return render_template('profile.html', active_user=active_user, sessionUser=sessionUser)

@app.get('/profile/edit')
def display_edit_profile():
    session_user = User.query.filter_by(username = session['username']).first()
    game_tags = GameTag.query.all()
    game_tag_names = [game_tag.game_tag_name for game_tag in game_tags]

    return render_template('profile_edit.html', session_user=session_user, game_tags=game_tag_names)

@app.post('/profile/edit')
def edit_profile():
    active_user = User.query.filter_by(username = session['username']).first()
    game_tags = GameTag.query.all()

    active_user.first_name = request.form.get('first_name')
    active_user.last_name = request.form.get('last_name', active_user.last_name)
    active_user.bio_text = request.form.get('bio_text')
    game_tag_names = request.form.getlist('game_tag_input')

    active_user.game_tags = []
    db.session.commit()

    match_tag = None
    for tag_name in game_tag_names:

        if not tag_name:
            continue

        for game_tag in game_tags:
            if game_tag.game_tag_name == tag_name:
                match_tag = game_tag
                break
        
        if match_tag is not None:
            active_user.game_tags.append(game_tag)
            match_tag = None
        else:
            print("miss")
            new_game_tag = GameTag(game_tag_name = tag_name)
            active_user.game_tags.append(new_game_tag)
    
    if 'profile_pic' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file')
    
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
        file.save(filename)
        link = upload_to_imgbb(filename)
        active_user.profile_pic = link
        session['profile_pic'] = active_user.profile_pic
        os.remove(filename)

    db.session.commit()
    return redirect('./' + str(active_user.user_id))

@app.get('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/forum', methods=('GET', 'POST'))
def forum():
    user_id = session.get('user_id')  # get the current user ID from session
    posts = ForumPost.query.filter(ForumPost.parent_post_id.is_(None)).order_by(ForumPost.time_posted.desc()).all()
    # display all parent posts in most-recent first order
    for post in posts:
        if not post.category:
            post.category = "None"
        post.category = ''.join(word.capitalize() for word in post.category.split('-'))
        vote = Vote.query.filter_by(voter_id=user_id, post_id=post.post_id).first()  # get the vote record for this user-post pair
        if vote:
            post.user_vote_status = vote.vote_status  # store the vote status in the post object
        else:
            post.user_vote_status = 0  # default to no vote
    description = get_forum_description('main')
    return render_template('forum.html', description=description, posts=posts)

@app.get('/forum/<category>')
def subforum(category):
    user_id = session.get('user_id')
    posts = ForumPost.query.filter(ForumPost.category.ilike(f'%{category}%'), ForumPost.parent_post_id.is_(None)).order_by(ForumPost.time_posted.desc()).all()
    for post in posts:
        post.category = ''.join(word.capitalize() for word in post.category.split('-'))
        vote = Vote.query.filter_by(voter_id=user_id, post_id=post.post_id).first()  # get the vote record for this user-post pair
        if vote:
            post.user_vote_status = vote.vote_status  # store the vote status in the post object
        else:
            post.user_vote_status = 0  # default to no vote
    description = get_forum_description(category)
    return render_template('subforum.html', category=category, description=description, posts=posts)

def category_to_url(category):
    category = re.sub(r'([a-z])([A-Z])', r'\1-\2', category)
    category = category.lower()
    category = category.replace(' ', '-')
    return category
# register the custom filter to the app's Jinja environment
app.jinja_env.filters['category_to_url'] = category_to_url

def get_forum_description(category):
    forum_description = ForumDescription.query.filter_by(category=category).first()
    if not forum_description:
        return "No description available"
    return forum_description.description

@app.get('/forum_post/<int:post_id>')
def get_single_post(post_id):
    user_id = session.get('user_id')  # get the current user ID from session
    post = ForumPost.query.get(post_id)
    vote = Vote.query.filter_by(voter_id=user_id, post_id=post.post_id).first()  # get the vote record for this user-post pair
    post.category = ''.join(word.capitalize() for word in post.category.split('-'))
    if post is None:
        return "Error: Post does not exist"
    if vote:
        post.user_vote_status = vote.vote_status  # store the vote status in the post object
    else:
        post.user_vote_status = 0  # default to no vote
    return render_template('get_single_post.html', post=post)

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

@app.post('/comment_post/<int:post_id>')
def comment_post(post_id):
    user_id = User.query.filter_by(user_id=session['user_id']).first()
    parent_post = ForumPost.query.get(post_id)
    if parent_post is None:
        # handle error: post not found
        pass
    comment_content = request.form.get('content')
    if comment_content is None or comment_content.strip() == '':
        # content cannot be empty
        pass
    comment = ForumPost(
        title=f"Re: {parent_post.title}",
        content=comment_content,
        author_id=user_id.user_id,
        parent_post_id=parent_post.post_id,
        category=parent_post.category
    )
    db.session.add(comment)
    db.session.commit()
    return redirect(request.referrer)

@app.get('/edit_post/<int:post_id>')
def edit_post(post_id):
    post = ForumPost.query.get(post_id)
    # check if the session username exists and matches the author of the post
    if 'username' not in session:
        return redirect(url_for('login')) # Redirect to the login page
    if session['username'] == post.author.username:
        return render_template('edit_post.html', post=post, prev_url=request.referrer)
    else:
        abort(403) # Forbidden

@app.post('/update_post')
def update_post():
    prev_url = request.form.get('prev_url')
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
    if prev_url and is_safe_url(prev_url):
        return redirect(prev_url)
    else:
        return redirect(url_for('get_single_post', post_id=post_id))

@app.post('/upvote')
def upvote_post():
    if 'user_id' not in session:
        return jsonify(success=False, message="You must log in to vote.")
    post_id = request.json.get('post_id')
    post = ForumPost.query.get(post_id)
    vote = Vote.query.get((session['user_id'], post_id))
    if post:
        if vote is None:
            vote = Vote(user_id=session['user_id'], post_id=post_id, vote_status=1)
            db.session.add(vote) # set user vote status to 1 and add to Vote table
            post.upvote() # increment posts total upvotes
        elif vote.vote_status == 0: # record of Vote exists but status is neutral
            vote.vote_status = 1 # change user status to +1
            post.upvote() # increment posts total upvotes
        elif vote.vote_status == -1: # if user had previously downvoted the post
            vote.vote_status = 0 # restore user's vote back to neutral
            post.upvote() # return one upvote back to total
        db.session.commit() # save changes to Vote and ForumPost tables
        return jsonify(success=True, vote_status=vote.vote_status)
    else:
        return jsonify(success=False, message="Oops! Something went wrong. Please try again."), 404

@app.post('/downvote')
def downvote_post():
    if 'user_id' not in session:
        return jsonify(success=False, message="You must log in to vote.")
    post_id = request.json.get('post_id')
    post = ForumPost.query.get(post_id)
    vote = Vote.query.get((session['user_id'], post_id))
    if post:
        if vote is None:
            vote = Vote(user_id=session['user_id'], post_id=post_id, vote_status=-1)
            db.session.add(vote) # set user vote status to -1 and add record of Vote to table
            post.downvote() # decrement posts total upvotes
        elif vote.vote_status == 0: # record of Vote exists but status is neutral
            vote.vote_status = -1 # change user status to -1
            post.downvote() # increment posts total upvotes
        elif vote.vote_status == 1: # if user had previously upvoted the post
            vote.vote_status = 0 # restore user's vote back to neutral
            post.downvote() # remove one upvote from total
        db.session.commit() # save changes to Vote and ForumPost tables
        return jsonify(success=True, vote_status=vote.vote_status)
    else:
        return jsonify(success=False, message="Oops! Something went wrong. Please try again."), 404

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

@app.get('/forum/search/', defaults={'category': None})
@app.get('/forum/search/<category>')
def search_posts(category):
    query_flair = request.args.get('query-flair', '')
    query_title = request.args.get('query-title', '')
    subforum = False
    query = ForumPost.query.filter(ForumPost.parent_post_id.is_(None)).order_by(ForumPost.time_posted.desc())
    if category:
        query = query.filter(ForumPost.category == category)
        subforum = True
    if query_flair:
        query = query.filter((ForumPost.flairs.ilike(f'%{query_flair}%')))
    if query_title:
        query = query.filter((ForumPost.title.ilike(f'%{query_title}%')))
    filtered_posts = query.order_by(ForumPost.time_posted.desc()).all()
    description = get_forum_description(category)
    if subforum == True:
       return render_template('subforum.html', category=category, description=description, posts=filtered_posts)

    return render_template('forum.html', description=get_forum_description('main'), posts=filtered_posts)

def get_forum_description(category):
    forum_description = ForumDescription.query.filter_by(category=category).first()
    if not forum_description:
        return "No description available"
    return forum_description.description

@app.post('/profile')
def new_player():
    return render_template('profile.html')

active_users = {}
game_inventories = {}

@app.route('/active_game')
def active_game():
    if 'username' in session:       
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            active_games = ActiveGame.query.filter_by(user_id=user.user_id).all()
            game_sessions = []
            for active_game in active_games:
                game_session = GameSession.query.filter_by(active_game_id=active_game.active_game_id).first()
                if game_session:
                    game_sessions.append(game_session)
            games = Game.query.all()
            return render_template('active_game.html', active_games=active_games, game_sessions=game_sessions, games=games, user=user)
        else:
            return render_template('error.html', error_message="User not found.")
    else:
        return redirect('login')
    
@app.route('/game_availability/<int:active_game_id>', methods=['POST'])
def game_availability(active_game_id):
    game_session = GameSession.query.get_or_404(active_game_id)
    username = session['username']
    user = User.query.filter_by(username=username).first()
    # Check if the logged-in user is the owner of the game session
    if game_session.owner == user.username:
        game_session.open_for_join = not game_session.open_for_join
        db.session.commit()
    return redirect(url_for('active_game'))

@app.route('/join_game', methods=['GET', 'POST'])
def join_game():
    if 'username' in session:
        username = session.get('username')
        user = User.query.filter_by(username=username).first()
        # Retrieve the user's active game IDs
        user_active_game_ids = [active_game.active_game_id for active_game in user.active_games]
        if request.method == 'POST':
            game_id_to_join = request.form.get('game_id')
            if game_id_to_join and game_id_to_join not in user_active_game_ids:
                active_game = ActiveGame(active_game_id=game_id_to_join, user_id=user.user_id)
                db.session.add(active_game)
                db.session.commit()
                return redirect(url_for('active_game'))
        games = Game.query.all()
        game_session = GameSession.query.all()
        return render_template('join_game.html', games=games, game_session=game_session, user_active_game_ids=user_active_game_ids)
    else:
        return redirect('login')

@app.route('/chatsession/<int:active_game_id>')
def chat(active_game_id):
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            is_user_in_active_game = ActiveGame.query.filter_by(user_id=user.user_id, active_game_id=active_game_id).first()

            if is_user_in_active_game:
                return render_template('chat_session.html', user=username, active_game_id=active_game_id)
            else:
                return redirect('/join_game')
    else:
        return redirect('/login')

@socketio.on('set_active_user')
def set_active_user(username):
    session['active_username'] = username
    socketio.emit('active_user_changed', username)

@socketio.on('connected')
def handle_connect(json):
    username = json.get('username')
    active_game_id = json.get('active_game_id')
    join_room(active_game_id)
    user = player_repository_singleton.get_user_by_username(username)
    if user:
        session['active_user_id'] = user.user_id
        session['active_game_id'] = active_game_id
        active_users.setdefault(active_game_id, set()).add(username)
        set_active_user(username)
        emit('active_users', {'active_users': list(active_users[active_game_id])}, room=active_game_id)
        game_session = GameSession.query.filter_by(active_game_id=active_game_id).first()
        if game_session and game_session.log:
            # Call add_last_inventory to populate the inventory with existing data
            print(game_session.log)
            log_data = jsons.loads(game_session.log)[0]
            print(log_data)
            game_inventories[active_game_id]=[]
            game_inventories[active_game_id].extend(log_data)
            socketio.emit('update_inventory', {'inventory': game_inventories[active_game_id], 'active_game_id': active_game_id}, room=active_game_id)           

@socketio.on('disconnect')
def handle_disconnect():
    active_username = session.get('active_username')
    active_game_id = session.get('active_game_id')
    if active_username and active_game_id in active_users:
        active_users[active_game_id].remove(active_username)
        socketio.emit('active_users', {'active_users': list(active_users[active_game_id])}, room=active_game_id)
        print(f"User {active_username} disconnected from room {active_game_id}.")
        leave_room(active_game_id)
        socketio.emit('disconnect_from_room', {'active_game_id': active_game_id, 'username': active_username}, room=active_game_id)

@socketio.on('message')
def handle_message(json):
    user_id = session.get('active_user_id')
    user = player_repository_singleton.get_user_by_id(user_id)
    if user:
        active_game_id = json.get('active_game_id')
        message = json.get('message')
        if message.startswith('!roll '):
            sides = int(message.split(' ')[1])
            roll_result = random.randint(1, sides)
            socketio.emit('message', {'username': 'Server', 'message': f'[{user.username}] performed a Dice Roll ({sides} sides) ! Result: {roll_result}', 'active_game_id': active_game_id}, room=active_game_id)
        elif message.startswith('!add '):
            items = message[5:].strip().split(',,')
            items = [item.strip() for item in items if item.strip()]
            if items:
                for item in items:
                    socketio.emit('message', {'username': 'Server', 'message': f'[{user.username}] has added to Game Log: {item} ', 'active_game_id': active_game_id}, room=active_game_id)
        
                add_items_to_inventory(user, active_game_id, items)
        elif message.startswith('!remove '):
            try:
                item_number = int(message.split(' ')[1])
                if 1 <= item_number <= len(game_inventories.get(active_game_id, [])):
                    remove_item_from_inventory(active_game_id, item_number)
            except (ValueError, IndexError):
                pass 
        else:
            socketio.emit('message', {'username': user.username, 'message': message, 'active_game_id': active_game_id}, room=active_game_id)

def remove_item_from_inventory(active_game_id, item_number):
    user_id = session.get('active_user_id')
    user = player_repository_singleton.get_user_by_id(user_id)
    game_session = GameSession.query.filter_by(active_game_id=active_game_id).first()
    if active_game_id in game_inventories:
        if 1 <= item_number <= len(game_inventories[active_game_id]):
            removed_item = game_inventories[active_game_id].pop(item_number - 1)
            socketio.emit('update_inventory', {'inventory': game_inventories[active_game_id], 'active_game_id': active_game_id}, room=active_game_id)
            socketio.emit('message', {'username': 'Server', 'message': f'[{user.username}] has removed from the Game Log: {removed_item["item_name"]}', 'active_game_id': active_game_id}, room=active_game_id)
            game_session.log = jsons.dumps([game_inventories[active_game_id]])
            db.session.commit()

def add_items_to_inventory(user, active_game_id, items):
    if active_game_id not in game_inventories:
        game_inventories[active_game_id] = []
    
    game_session = GameSession.query.filter_by(active_game_id=active_game_id).first()
    print(game_inventories)

    for item_name in items:
        game_inventories[active_game_id].append({'username': user.username, 'item_name': item_name})
        game_session.log = jsons.dumps([game_inventories[active_game_id]])
        db.session.commit()

    socketio.emit('update_inventory', {'inventory': game_inventories[active_game_id], 'active_game_id': active_game_id}, room=active_game_id)

def add_last_inventory(user, active_game_id, items):
    game_inventories[active_game_id] = []
    # game_session = GameSession.query.filter_by(active_game_id=active_game_id).first()
    # if game_session and game_session.log:
    #     log_data = jsons.loads(game_session.log)
    #     game_inventories[active_game_id].extend(log_data)
    for item_name in items:
        game_inventories[active_game_id].append({'username': user.username, 'item_name': item_name})
    socketio.emit('update_inventory', {'inventory': game_inventories[active_game_id], 'active_game_id': active_game_id}, room=active_game_id)

# Handle file upload
@app.route("/upload", methods=["POST"])
def upload():
    if "photo" in request.files:
        photo = request.files["photo"]
        if photo.filename == "":
            return jsonify({"error": "No file selected"}), 400
        filename = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(photo.filename))
        photo.save(filename)
        imgbb_url = upload_to_imgbb(filename)
        socketio.emit("image_uploaded", {"url": imgbb_url})
        os.remove(filename)

        return jsonify({"url": imgbb_url})

    return jsonify({"error": "No file provided"}), 400

def upload_to_imgbb(filename):
    imgbb_api_key = {os.getenv("IMGBB")}
    imgbb_url = "https://api.imgbb.com/1/upload"
    files = {"image": (filename, open(filename, "rb"))}
    params = {"key": imgbb_api_key}
    response = requests.post(imgbb_url, files=files, params=params)
    result = response.json()

    if result["success"]:
        return result["data"]["url"]
    else:
        return None
    
@app.route('/create_game', methods=['GET', 'POST'])
def create_game():
    if request.method == 'POST':
        # Get form data
        game = request.form.get('game')
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('image')  # Use .get() to avoid KeyError if 'image' is not present
        imgbb_url = None  # Default or placeholder image URL
        if file and file.filename != '':
            imgbb_url = upload_to_imgbb(file)
        # Create a new game record
        game_exists = Game.query.filter_by(game=game).first()
        if game_exists:
            username = session.get('username')
            user = User.query.filter_by(username=username).first()
            if user:
                new_game_session = GameSession(title=title, game_id=game_exists.game_id, open_for_join=True, owner=username, image=imgbb_url)
                db.session.add(new_game_session)
                db.session.commit()
                new_active_game = ActiveGame(active_game_id=new_game_session.active_game_id, user_id=user.user_id)
                db.session.add(new_active_game)
                db.session.commit()
                return redirect(url_for('join_game'))
        else:
            new_game = Game(game=game, description=description)
            db.session.add(new_game)
            db.session.commit()
            print(f"Game '{game}' added to the database.")
            username = session.get('username')
            user = User.query.filter_by(username=username).first()
            if user:
                new_game_session = GameSession(title=title, game_id=new_game.game_id, open_for_join=True, owner=username, image=imgbb_url)
                db.session.add(new_game_session)
                db.session.commit()
                new_active_game = ActiveGame(active_game_id=new_game_session.active_game_id, user_id=user.user_id)
                db.session.add(new_active_game)
                db.session.commit()
            return redirect(url_for('join_game'))
    # Fetch all games from the database
    games = Game.query.all()
    return render_template('create_game.html', games=games)

@app.get('/devblog')
def goto_devblog():
    return render_template('devblog.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    socketio.run(app, debug=True)
