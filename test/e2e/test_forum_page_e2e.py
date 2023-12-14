import pytest
from flask.testing import FlaskClient
from app import app

@pytest.fixture()
def test_app() -> FlaskClient:
    return app.test_client()

def test_forum_topics(test_app: FlaskClient) -> None:
    response = test_app.get('/forum')
    assert response.status_code == 200
    assert b'<a href="/forum/community-square"' in response.data
    assert b'<a href="/forum/looking-for-group"' in response.data
    assert b'<a href="/forum/creative-content"' in response.data
    assert b'<a href="/forum/gamemaster-corner"' in response.data
    assert b'<a href="/forum/bug-report-technical"' in response.data
    assert b'<a href="/forum"' in response.data
    
def test_check_forum_description_exist(test_app: FlaskClient) -> None:
    response = test_app.get('/forum')
    assert response.status_code == 200
    assert b'<p class="card-text">All Topics - GuildBoard Main: Your one-stop destination for general discussions, announcements, and everything else not covered in other categories.</p>'