from models import db, User

class UserRepository:

    def get_all_users(self):
            return User.query.all()
        
    def get_user_by_id(self, user_id: int) -> User | None:
            return User.query.get(user_id)
    
    def get_user_by_username(self, username: str) -> User | None:
        return User.query.filter_by(username=username).first()
        
user_repository_singleton = UserRepository()