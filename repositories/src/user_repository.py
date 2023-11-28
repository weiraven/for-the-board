from models import db, User

class UserRepository:

    def get_all_users(self):
            return User.query.all()
        
    def get_user_by_id(self, user_id: int) -> User | None:
            return User.query.get(user_id)
    
    def get_user_by_username(self, username: str) -> User | None:
        return User.query.filter_by(username=username).first()

    def get_user(self, user_id):
        one_user = User.query.get(user_id)
        return one_user
    
    def create_user(self, user_id, username, email, password, date_created):
        new_user = User(user_id=user_id, username=username, email=email, password=password, date_created=date_created)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def search_user(self, username):
        return User.query.filter(User.username.ilike(f'%{username}%')).all()
    
player_repository_singleton = UserRepository()