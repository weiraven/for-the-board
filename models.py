from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped
from datetime import datetime
from dataclasses import dataclass

db = SQLAlchemy()

UserGames = db.Table('usergames',
    db.Column('user_id', db.Integer, db.ForeignKey('player.user_id')),
    db.Column('game_tag_id', db.Integer, db.ForeignKey('gametag.game_tag_id'))
    )

@dataclass
class GameTag(db.Model):
    __tablename__ = 'gametag'
    game_tag_id = db.Column(db.Integer, primary_key=True)
    game_tag_name = db.Column(db.String(255), nullable=False, unique=True)

class User(db.Model):
    __tablename__ = 'player'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(255), nullable=True)
    bio_text = db.Column(db.Text, nullable=True, default='Sample Text')
    posts = db.relationship('ForumPost', backref='author', lazy='dynamic')
    game_tags = db.relationship('GameTag', secondary=UserGames, backref='users')
    
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

    # need to also delete vote data when associated post is deleted from db
    votes = db.relationship('Vote', backref='forumpost', cascade='all, delete-orphan')
    comments = db.relationship('ForumPost', backref=db.backref('parent', remote_side=[post_id]), lazy='dynamic')

    # forumpost constructor
    def __init__(self, title:str, content:str, author_id:int, flairs='', parent_post_id=None,category='') -> None:
        self.title = title
        self.content = content
        self.author_id = author_id
        self.upvotes = 0
        self.flairs = flairs
        self.parent_post_id = parent_post_id
        self.category = category

    # tabulate how many comments a post has
    def count_comments(self):
        return ForumPost.query.filter_by(parent_post_id=self.post_id).count()

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
    
    def get_category(self) -> str:
        return self.category

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

class ForumDescription(db.Model):
    __tablename__ = 'forum_description'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text)

    def __init__(self, category:str, description:str) -> None:
            self.category = category
            self.description = description

class Vote(db.Model):
    __tablename__ = 'vote'
    voter_id = db.Column(db.Integer, db.ForeignKey('player.user_id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forumpost.post_id'), primary_key=True)
    vote_status = db.Column(db.Integer, default=0) # 1 for upvote, -1 for downvote, 0 for no vote

    def __init__(self, user_id:int, post_id:int, vote_status:int=0) -> None:
            self.voter_id = user_id
            self.post_id = post_id
            self.vote_status = vote_status

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
    __tablename__ = 'activegame'

    active_game_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('player.user_id'), nullable=False)

    def get_active_game_id(self) -> int:
        return self.active_game_id

    def get_user_id(self) -> int:
        return self.user_id

    def __repr__(self) -> str:
        return f'ActiveGame({self.active_game_id}, {self.user_id})'

class GameSession(db.Model):
    __tablename__ = 'gamesession'

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





#class UserGames(db.Model):
#    user_game_id = db.Column(db.Integer, primary_key=True)
#    user_id = db.Column(db.Integer, db.ForeignKey('player.user_id'))
#    game_id = db.Column(db.Integer, db.ForeignKey('GameTag.game_tag_id'))