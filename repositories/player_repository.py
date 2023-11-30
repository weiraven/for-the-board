from models import db, Player

class PlayerRepository:

    def get_player(self, user_id):
        one_user = Player.query.get(user_id)
        return one_user
    
    def create_player(self, user_id, username, email, password, date_created):
        new_user = Player(user_id=user_id, username=username, email=email, password=password, date_created=date_created)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def search_player(self, username):
        return Player.query.filter(Player.username.ilike(f'%{username}%')).all()