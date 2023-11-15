import os
from flask import Flask, render_template, request, redirect, url_for
from models import *
from dotenv import load_dotenv
from flask_socketio import SocketIO

load_dotenv()
app = Flask(__name__)

# DB connection
app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

db.init_app(app)

socketio = SocketIO(app)

@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')


@app.route('/forum', methods=('GET', 'POST'))
def forum():
    posts = ForumPost.query.order_by(ForumPost.time_posted.desc()).all()
    # display all posts in most-recent first order
    return render_template('forum.html', posts=posts)

# @app.get('/chatsession')
# def chat():
#     return render_template('chat_session.html', users=users)

# @socketio.on('set_active_user')
# def set_active_user(user_id):
#     global active_user_id
#     active_user_id = user_id
#     socketio.emit('active_user_changed', user_id)

# @socketio.on('connected')
# def handle_connect(json):
#     username = json.get('username')
#     user_id = None
#     for uid, uname in users.items():
#         if uname == username:
#             user_id = uid
#             break
#     if user_id:
#         set_active_user(user_id)


# @socketio.on('message')
# def handle_message(json):
#     username = users.get(active_user_id)  # Get the username based on active_user_id
#     if username:
#         socketio.emit('message', {'username': username, 'message': json['message']})

# @app.get('/forum/<int:post_id>')
# def get_single_post(post_id: int):
#     return render_template('get_single_post.html')

# @app.post('/submit_post')
# def submit_forum_post():
#     # after post, redirect back to forum.html. maybe redirect to this post new page (get_single_forum)
#     author = request.form['author']
#     title = request.form['title']
#     content = request.form['content']
#     hours_posted = '14 hours'
#     avatar = 'https://i.kym-cdn.com/entries/icons/facebook/000/014/711/neckbeard.jpg'
#     id = int(len(dummy_data) + 1)
#     dummy_data.append({id, title, content, author, hours_posted, avatar})
#     return redirect('/forum.html')

# @app.post('/submit_forum_reply')
# def submit_forum_reply():
#     # after post, redirect back to get_single_post.html
#     return render_template('forum.html')

@app.get('/create_account')
def create_account():
    return render_template('create_account.html')

@app.get('/create_post')
def create_post():
    return render_template('create_post.html')

# if __name__ == '__main__':
#     socketio.run(app, debug=True)
