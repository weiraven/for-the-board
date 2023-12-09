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
    upvotes = db.Column(db.Integer, default=0)
    flairs = db.Column(db.String(255))
    parent_post_id = db.Column(db.Integer, db.ForeignKey('forumpost.post_id'))
    category = db.Column(db.String(255))

    # forumpost constructor
    def __init__(self, title:str, content:str, author_id:int, flairs='', parent_post_id=None,category='') -> None:
        self.title = title
        self.content = content
        self.author_id = author_id
        self.upvotes = 0
        self.flairs = flairs
        self.parent_post_id = parent_post_id
        self.category = category

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
        # return self.time_posted.strftime('%m-%d-%Y %H:%M')
        return self.time_posted.isoformat()

    def get_upvotes(self) -> int:
        return self.upvotes

    def get_parent_post_id(self):
        return self.parent_post_id
    
    def get_flairs(self):
        return self.flairs
    
    def get_category(self):
        return self.category
    
    # other methods
    def upvote(self):
        self.upvotes += 1
        db.session.commit()
    
    def downvote(self):
        if self.upvotes > 0:
            self.upvotes -= 1
            db.session.commit()

class Game(db.Model):
    __tablename__ = 'game'
    game_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game = db.Column(db.String(255), nullable=False, unique=True)   
    description = db.Column(db.Text)

    def __init__(self, game: str, description: str) -> None:
        self.game = game
        self.description = description

    def get_game_id(self) -> int:
        return self.game_id

    def get_game(self) -> str:
        return self.game

    def get_description(self) -> str:
        return self.description

    def set_game(self, game: str):
        self.game = game

    def set_description(self, description: str):
        self.description = description

    def __repr__(self) -> str:
        return f'Game({self.game_id}, {self.game})'
    
class ActiveGame(db.Model):
    __tablename__ = 'active_game'

    active_game_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('player.user_id'), nullable=False)

    def get_active_game_id(self) -> int:
        return self.active_game_id

    def get_user_id(self) -> int:
        return self.user_id

    def __repr__(self) -> str:
        return f'ActiveGame({self.active_game_id}, {self.user_id})'

class GameSession(db.Model):
    __tablename__ = 'game_session'

    active_game_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.game_id'), nullable=False)
    open_for_join = db.Column(db.Boolean, default=True, nullable=False)
    title = db.Column(db.String(255), nullable=False) 

    def get_active_game_id(self) -> int:
        return self.active_game_id

    def get_game_id(self) -> int:
        return self.game_id
    
    def get_title(self) -> str:
        return self.title

    def is_open_for_join(self) -> bool:
        return self.open_for_join
    
    def set_title(self, title: str):
        self.title = title

    def set_open_for_join(self, open_for_join: bool) -> None:
        self.open_for_join = open_for_join

    def __repr__(self) -> str:
        return f'GameSession({self.active_game_id}, {self.game_id}, {self.open_for_join},  {self.title})'