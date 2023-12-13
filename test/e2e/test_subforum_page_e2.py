import pytest
from flask.testing import FlaskClient
from app import app

@pytest.fixture()
def test_app() -> FlaskClient:
    return app.test_client()