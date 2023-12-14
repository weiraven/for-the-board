import pytest
from flask.testing import FlaskClient
from app import app
from models import Game, GameSession, ActiveGame, User, db

@pytest.fixture
def test_app() -> FlaskClient:
    return app.test_client()

def test_create_game(test_app: FlaskClient) -> None:
    response = test_app.post('/create_game', data={
        'game': 'test_game',
        'title': 'Test Game Title',
        'description': 'Test Game Description'
    }, content_type='multipart/form-data')

    # Check if the request was successful (redirect to 'join_game')
    assert response.status_code == 302
    assert response.location == 'http://localhost/join_game'

    # Check if the game was added to the database
    with app.app_context():
        game = Game.query.filter_by(game='test_game').first()
        assert game is not None

        # Check if the game session and active game were created
        game_session = GameSession.query.filter_by(game_id=game.game_id).first()
        assert game_session is not None

        active_game = ActiveGame.query.filter_by(active_game_id=game_session.active_game_id).first()
        assert active_game is not None

def test_join_game(test_app: FlaskClient):
    # Set up a user for testing
    with app.app_context():
        user = User(username='testuser', password='testpassword', first_name='Test', last_name='User', email='testuser@example.com')
        db.session.add(user)
        db.session.commit()

    # Log in the test user
    response_login = test_app.post('/login', data=dict(username='testuser', password='testpassword'))

    # Check if the login was successful (redirects to 'join_game')
    assert response_login.status_code == 302
    assert response_login.location == 'http://localhost/join_game'


    response_join_game = test_app.post('/join_game', data={'game_id': '1'})

    # Check if the request was successful (redirects to 'active_game')
    assert response_join_game.status_code == 302
    assert response_join_game.location == 'http://localhost/active_game'

    # Check if the user joined the game 
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None

        # Check if the active game record was created for the user
        active_game = ActiveGame.query.filter_by(user_id=user.user_id, active_game_id=1).first()
        assert active_game is not None
