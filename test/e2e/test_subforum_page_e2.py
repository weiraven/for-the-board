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
    
    response = test_app.get('/forum/community-square')
    assert response.status_code == 200
    assert b'<p class="card-text">Welcome to the Community Square - the bustling heart of our forum where players and enthusiasts come together. Share your experiences, discuss the latest in tabletop gaming, and connect with fellow adventurers.</p>'
    
    response = test_app.get('forum/bug-report-technical')
    assert response.status_code == 200
    assert b'<p class="card-text">Encountered a bug or facing technical issues? Report them here and get assistance. Help us improve the forum experience for all.</p>'
    
# def test_search_in_specific_subforum(test_app: FlaskClient) -> None:
    
# def test_edit_flair_in_post(test_app: FlaskClient) -> None:
    
# def test_update_flair_in_post(test_app: FlaskClient) -> None:
    
# def test_edit_post(test_app: FlaskClient) -> None:
    