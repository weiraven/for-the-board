from models import db, Game, ActiveGame, GameSession

class GameRepository:

    def get_all_games(self):
        return Game.query.all()

    def get_game_by_id(self, game_id: int) -> Game | None:
        return Game.query.get(game_id)

    def create_game(self, title, description):
        new_game = Game(title=title, description=description)
        db.session.add(new_game)
        db.session.commit()
        return new_game

    def get_active_game_by_user_id(self, user_id: int) -> ActiveGame | None:
        return ActiveGame.query.filter_by(user_id=user_id).first()

    def create_active_game(self, user_id: int):
        new_active_game = ActiveGame(user_id=user_id)
        db.session.add(new_active_game)
        db.session.commit()
        return new_active_game

    def get_game_session_by_id(self, active_game_id: int) -> GameSession | None:
        return GameSession.query.get(active_game_id)

    def create_game_session(self, game_id: int, open_for_join: bool = True):
        new_game_session = GameSession(game_id=game_id, open_for_join=open_for_join)
        db.session.add(new_game_session)
        db.session.commit()
        return new_game_session
    
game_repository_singleton = GameRepository()

