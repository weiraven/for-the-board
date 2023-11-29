from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'player'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('ForumPost', backref='author', lazy='dynamic')

    # User constructor
    def __init__(self, first_name:str, last_name:str, email:str, username:str, password:str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password = password
        
    # User getters
    def get_id(self) -> int:
        return self.user_id

    def get_first_name(self) -> str:
        return self.first_name

    def get_last_name(self) -> str:
        return self.last_name

    def get_username(self) -> str:
        return self.username

    def get_email(self) -> str:
        return self.email
    
    def get_join_date(self):
        return self.date_created.strftime('%B %d, %Y')
    
    # dunder method override for how user info prints
    def __repr__(self) -> str:
        return f'Player({self.user_id}, {self.username}, {self.email})'

class ForumPost(db.Model):
    __tablename__ = 'forumpost'
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('player.user_id'))
    time_posted = db.Column(db.DateTime, default=datetime.utcnow)
    upvotes = db.Column(db.Integer)
    parent_post_id = db.Column(db.Integer, db.ForeignKey('forumpost.post_id'))
    flairs = db.Column(db.String(255))

    # forumpost constructor
    def __init__(self, title:str, content:str, author_id:int, flairs='', parent_post_id=None) -> None:
        self.title = title
        self.content = content
        self.author_id = author_id 
        self.flairs = flairs
        # should be replaced by author_id which would populate automatically from auth token
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

    def get_time_posted(self):
        return self.time_posted.strftime('%m-%d-%Y %H:%M (UTC-5)')

    def get_upvotes(self) -> int:
        return self.upvotes

    def get_parent_post_id(self):
        return self.parent_post_id
    
    def get_flairs(self):
        return self.flairs

    # forumpost setters
    def set_title(self, title:str):
        self.title = title

    def set_content(self, content:str):
        self.content = content

    def set_author_id(self, author_id:int):
        self.author_id = author_id

    def set_upvotes(self, upvotes:int):
        self.upvotes = upvotes

    def set_parent_post_id(self, parent_post_id:int):
        self.parent_post_id = parent_post_id