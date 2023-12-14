import pytest
from flask.testing import FlaskClient
from flask import url_for
from app import app

@pytest.fixture()
def test_app() -> FlaskClient:
    return app.test_client()

def test_create_game(test_app: FlaskClient) -> None:
    with app.test_request_context():
        
        url = url_for('create_game')


    response = test_app.get(url, follow_redirects=True)


    assert response.status_code == 200

def test_active_game(test_app: FlaskClient) -> None:
    with app.test_request_context():

        url = url_for('active_game')


    response = test_app.get(url, follow_redirects=True)


    assert response.status_code == 200

def test_join_game(test_app: FlaskClient) -> None:
    with app.test_request_context():
 
        url = url_for('join_game')


    response = test_app.get(url, follow_redirects=True)


    assert response.status_code == 200