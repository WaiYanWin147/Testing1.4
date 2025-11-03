import pytest
from app import create_app, db
from app.entity.user_account import UserAccount

@pytest.fixture()
def app():
    # Use an in-memory database for testing
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        #Create a dummy user that matches your actual model
        user = UserAccount(
            name="Demo User",
            email="demo@example.com",
            age=25,
            phoneNumber="1234567890",
            profileID=1,   # You might need to adjust this if FK constraint applies
        )
        user.password = "1234"  # uses your password property setter
        db.session.add(user)
        db.session.commit()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_user_password_hash(app):
    """Ensure password hashing and check_password work"""
    with app.app_context():
        user = UserAccount.query.first()
        # the _password field should not be equal to plain text
        assert user._password != "1234"
        # check_password should return True
        assert user.check_password("1234") is True
        # wrong password should fail
        assert user.check_password("wrong") is False


def test_user_get_id(app):
    """Ensure get_id returns string version of userID"""
    with app.app_context():
        user = UserAccount.query.first()
        assert isinstance(user.get_id(), str)
        assert user.get_id() == str(user.userID)
