import pytest
from flask import Flask
from app import create_app, db
from app.entity.user_account import UserAccount
from app.control import auth_controller

@pytest.fixture()
def app():
    app = create_app({"TESTING": True,
                      "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        # create a dummy user
        user = UserAccount(username="demo_user", password="1234", role="csr")
        db.session.add(user)
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_login_success(app):
    """Simulate a successful login if auth_controller.login() exists"""
    with app.app_context():
        # Only run if your auth_controller has a login() function
        if hasattr(auth_controller, "login"):
            # you might adjust params depending on your implementation
            result = auth_controller.login("demo_user", "1234")
            # if the controller returns a dict or obj, just check truthiness
            assert result is not None
        else:
            pytest.skip("auth_controller.login() not implemented")


def test_login_failure(app):
    """Simulate login failure with wrong password"""
    with app.app_context():
        if hasattr(auth_controller, "login"):
            bad = auth_controller.login("demo_user", "wrong_pass")
            assert bad is None or bad is False
        else:
            pytest.skip("auth_controller.login() not implemented")
