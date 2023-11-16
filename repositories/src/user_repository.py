from models import db, Player

class PlayerRepository:

    def get_all_users(self):
            return Player.query.all()
        
    def get_user_by_id(self, user_id: int) -> Player | None:
            return Player.query.get(user_id)
    
    def get_user_by_username(self, username: str) -> Player | None:
        return Player.query.filter_by(username=username).first()
        
player_repository_singleton = PlayerRepository()