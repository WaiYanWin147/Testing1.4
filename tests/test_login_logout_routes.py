import pytest
from app import create_app, db
from app.entity.user_profile import UserProfile
from app.entity.user_account import UserAccount

@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,   # disable CSRF for form posts in tests
    })
    with app.app_context():
        db.create_all()

        # ---- Create the smallest possible valid Profile row ----
        # Do NOT pass unknown kwargs like fullName – we don't know model fields.
        profile = UserProfile()
        db.session.add(profile)
        db.session.flush()   # ensure profile.profileID exists

        # ---- Create a user that links to the profile ----
        user = UserAccount(
            name="Demo User",
            email="demo@example.com",
            age=25,
            phoneNumber="1234567890",
            profileID=profile.profileID,   # satisfy FK
        )
        user.password = "1234"  # hashes via the property setter
        db.session.add(user)
        db.session.commit()
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_login_logout_flow(client):
    # 1) login with valid credentials
    resp = client.post("/login", data={"email": "demo@example.com", "password": "1234"}, follow_redirects=False)
    assert resp.status_code in (200, 302)

    # 2) session should contain _user_id (Flask-Login)
    with client.session_transaction() as sess:
        assert "_user_id" in sess and str(sess["_user_id"]).isdigit()

    # 3) logout
    resp2 = client.get("/logout", follow_redirects=False)
    assert resp2.status_code in (200, 302)

    # 4) session cleared
    with client.session_transaction() as sess:
        assert "_user_id" not in sess

def test_login_rejects_bad_password(client):
    resp = client.post("/login", data={"email": "demo@example.com", "password": "WRONG"}, follow_redirects=False)
    # could be 200 with error message, or 400/401, or 302 redirect to login
    assert resp.status_code in (200, 400, 401, 302)

    with client.session_transaction() as sess:
        assert "_user_id" not in sess
