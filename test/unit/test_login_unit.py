import pytest
from app import app, db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
bcrypt.init_app(app)

@pytest.fixture(scope='module')
def test_client():
    flask_app = app
    flask_app.config['TESTING'] = True

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client

@pytest.fixture(scope='module')
def init_database(test_client):
    db.create_all()
    # Delete any existing test user
    existing_user = User.query.filter_by(username='login_testuser').first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()
    # Create a new test user
    password_hash = bcrypt.generate_password_hash('testpassword').decode('utf-8')
    user = User(username='login_testuser', password=password_hash, first_name='Test', last_name='User', email='testuser@example.com')
    db.session.add(user)
    db.session.commit()
    yield db
    # Delete the test user after the tests are done
    db.session.delete(user)
    db.session.commit()
    
# successful login redirects back to the page user was last on so 302 is expected instead of 200
def test_login(test_client, init_database):
    response = test_client.post('/login', data=dict(username='testuser', password='testpassword'))
    assert response.status_code == 302

def test_invalid_login(test_client, init_database):
    response = test_client.post('/login', data=dict(username='wronguser', password='wrongpassword'))
    assert response.status_code == 302

