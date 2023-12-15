import pytest
from flask.testing import FlaskClient
from app import app

@pytest.fixture()
def test_app() -> FlaskClient:
    return app.test_client()

def test_forum_route(test_app: FlaskClient) -> None:
    response = test_app.get('/forum')
    assert response.status_code == 200
    
def test_create_post_route_unauthorized_access(test_app: FlaskClient) -> None:
    response = test_app.get('/create_post')
    assert response.status_code == 302
    
def test_forum_search_route(test_app: FlaskClient) -> None:
    response = test_app.get('/forum/search/')
    assert response.status_code == 200