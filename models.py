from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'player'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # player constructor
    def __init__(self, username:str, email:str, password:str):
        self.username = username
        self.email = email
        self.password = password
        
    # user getters
    def get_id(self) -> int:
        return self.user_id

    def get_username(self) -> str:
        return self.username

    def get_email(self) -> str:
        return self.email
    
    def get_join_date(self):
        return self.date_created.strftime('%B %d, %Y')
    
    # check password
    def check_password(self, password:str) -> bool:
        return self.password == password
    
    # dunder method override for how user info prints
    def __repr__(self) -> str:
        return f'Player({self.user_id}, {self.username}, {self.email})'

class ForumPost(db.Model):
    __tablename__ = 'forumpost'
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('player.user_id'))
    author_name = db.Column(db.String(255))
    time_posted = db.Column(db.DateTime, default=datetime.utcnow)
    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    parent_post_id = db.Column(db.Integer, db.ForeignKey('forumpost.post_id'))

    # forumpost constructor
    def __init__(self, title:str, content:str, author_id:int, parent_post_id=None):
        self.title = title
        self.content = content
        self.author_id = author_id
        self.parent_post_id = parent_post_id

    # forumpost getters
    def get_post_id(self) -> int:
        return self.post_id

    def get_title(self) -> str:
        return self.title

    def get_content(self) -> str:
        return self.content

    def get_author_id(self) -> int:
        return self.author_id

    def get_author_name(self) -> str:
        return self.author_name

    def get_time_posted(self):
        return self.time_posted.strftime('%m-%d-%Y %H:%M (UTC-5)')

    def get_upvotes(self) -> int:
        return self.upvotes

    def get_downvotes(self) -> int:
        return self.downvotes

    def get_parent_post_id(self):
        return self.parent_post_id

    # forumpost setters
    def set_title(self, title:str):
        self.title = title

    def set_content(self, content:str):
        self.content = content

    def set_author_id(self, author_id:int):
        self.author_id = author_id

    def set_author_name(self, author_name:str):
        self.author_name = author_name

    def set_upvotes(self, upvotes:int):
        self.upvotes = upvotes

    def set_downvotes(self, downvotes:int):
        self.downvotes = downvotes

    def set_parent_post_id(self, parent_post_id:int):
        self.parent_post_id = parent_post_id