import pytest
from app import app, db, User
from flask import session

@pytest.fixture(scope='module')
def test_client():
    flask_app = app
    flask_app.config['TESTING'] = True

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client

# Create a test user for the app
@pytest.fixture
def test_user():
    # Delete the test user if it already exists
    existing_user = User.query.filter_by(username='testuser').first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()
    # Create a new test user
    test_user = User('Test', 'User', 'test@example.com', 'testuser', 'testpassword')
    db.session.add(test_user)
    db.session.commit()
    return test_user

# Test the signup page GET request
def test_signup_get(test_client):
    response = test_client.get('/signup')
    assert response.status_code == 200
    assert b'Sign Up' in response.data

# Test the signup page POST request with existing email
def test_signup_post_existing_email(test_client, test_user):
    # Clear the session
    with test_client.session_transaction() as sess:
        sess.clear()
    response = test_client.post('/signup', data={'first_name': 'Bob', 'last_name': 'Jones', 'email': 'test@example.com', 'username': 'bobjones', 'password': 'bobsecret'})
    assert response.status_code == 200 # Render signup page again
    assert b'This email already exists. Please login.' in response.data
    assert 'username' not in session

# Test the signup page POST request with existing username
def test_signup_post_existing_username(test_client, test_user):
    # Clear the session
    with test_client.session_transaction() as sess:
        sess.clear()
    response = test_client.post('/signup', data={'first_name': 'Charlie', 'last_name': 'Brown', 'email': 'charlie@example.com', 'username': 'testuser', 'password': 'charliesecret'})
    assert response.status_code == 200 # Render signup page again
    assert b'Username is taken. Please choose another.' in response.data
    assert 'username' not in session
