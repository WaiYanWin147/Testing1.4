import pytest
from app import create_app, db
from app.entity.user_account import UserAccount

@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    with app.app_context():
        db.create_all()
        u = UserAccount(
            name="Demo User",
            email="demo@example.com",
            age=25,
            phoneNumber="123456789",
            profileID=1
        )
        u.password = "1234"
        db.session.add(u)
        db.session.commit()
    yield app

def test_intentional_fail_wrong_password(app):
    """Intentional failing test (expect wrong password to pass)."""
    with app.app_context():
        user = UserAccount.query.first()
        # ❌ Intentionally wrong expectation
        assert user.check_password("wrong") is True
