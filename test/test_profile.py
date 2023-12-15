import pytest
from flask.testing import FlaskClient
from random import seed
from random import random
from app import app

@pytest.fixture()
def test_app() -> FlaskClient:
    return app.test_client()

def test_profile_load(test_app: FlaskClient) -> None:
    signup, login = make_test_user()
    test_app.post('/signup', data = signup)
    test_app.post('/login', data = login)
    response = test_app.get("/profile/1")
    assert response.status_code == 200

def test_profile_miss(test_app: FlaskClient) -> None:
    response = test_app.get("/profile/-1")
    assert response.status_code == 404

def test_profile_edit(test_app: FlaskClient) -> None:
    signup, login = make_test_user()
    test_app.post('/signup', data = signup)
    test_app.post('/login', data = login)
    response = test_app.post('profile/edit', data = {
        'first_name':'new'
    })
    assert response.status_code == 302


def make_test_user():
    seed(12)
    random_num = random()

    test_user_signup = {
        'username':'Rachel_test_user' + str(random_num),
        'password':'abc123',
        'email':'revans35+test' + str(random_num) + '@uncc.edu',
        'first_name':'Rachel_test',
        'last_name':'test_user'
    }

    test_user_login = {
        'username':'Rachel_test_user' + str(random_num),
        'password':'abc123'
    }

    return test_user_signup, test_user_login