import os
from flask import Flask, render_template, request, redirect, url_for
from models import db
from dotenv import load_dotenv
from flask_socketio import SocketIO

load_dotenv()
app = Flask(__name__)

# DB connection
app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f'postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}'

db.init_app(app)

socketio = SocketIO(app)

users = {
    1: 'Damon Nitsavong',
    2: 'Phillip Chang',
    3: 'Raven Wei',
    4: 'Rachel ?',
    5: 'Thomas ?',
    6: 'Brandon Hach',
}

active_user_id = 1

dummy_data = [
    {
        'id': 1,
        'title': 'Dwarves are gey, lemme explain',
        'content': 'I rest my case.',
        'author': 'John Doe',
        'hours_posted': '167',
        'avatar': 'https://i.kym-cdn.com/entries/icons/facebook/000/014/711/neckbeard.jpg',
    },
    {
        'id': 2,
        'title': 'Dwarves are not gey, don't lemme explain',
        'content': 'I rest.',
        'author': 'Doe John',
        'hours_posted': '167',
        'avatar': 'https://i.kym-cdn.com/entries/icons/facebook/000/014/711/neckbeard.jpg',
    },
]


@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')


@app.get('/forum')
def forum():
    # Needs to display forum components from db
    return render_template('forum.html', posts=dummy_data)


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


@app.get('/forum/<int:forum_id>')
def get_single_forum(forum_id: int):
    # brings a new page that display specific forum post
    forum_post = dummy_data[forum_id]
    return render_template('get_single_forum.html', forum=forum_post)


@app.post('/submit_post')
def submit_forum_post():
    # after post, redirect back to forum.html. maybe redirect to this post new page (get_single_forum)
    author = request.form['author']
    title = request.form['title']
    content = request.form['content']
    hours_posted = '14 hours'
    avatar = 'https://i.kym-cdn.com/entries/icons/facebook/000/014/711/neckbeard.jpg'
    id = int(len(dummy_data) + 1)
    dummy_data.append({id, title, content, author, hours_posted, avatar})
    return redirect('/forum')


@app.post('/submit_comment')
def submit_forum_comment():
    # after post, redirect back to get_single_form.html
    return render_template('forum.html')


@app.get('/createAccount')
def account():
    return render_template('account.html')


@app.get('/create_post')
def create_post():
    return render_template('create_post.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)
