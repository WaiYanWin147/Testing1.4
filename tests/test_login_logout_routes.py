import pytest
from app import create_app, db
from app.entity.user_profile import UserProfile
from app.entity.user_account import UserAccount

@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,  # allow form posts
    })
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def _seed_user():
    """
    Create the minimum valid Profile + User.
    Your schema requires user_profiles.profileName NOT NULL,
    so we set it explicitly.
    """
    profile = UserProfile(
        profileName="Demo Profile",        # REQUIRED by your schema
        # description="optional",          # include if your model requires
        # isActive=True,                   # include if your model requires
    )
    db.session.add(profile)
    db.session.flush()  # get profile.profileID

    user = UserAccount(
        name="Demo User",
        email="demo@example.com",
        age=25,
        phoneNumber="1234567890",
        profileID=profile.profileID,       # satisfy FK
    )
    user.password = "1234"                 # property setter hashes
    db.session.add(user)
    db.session.commit()
    return user, profile

def test_login_logout_flow(app, client):
    with app.app_context():
        _seed_user()

    # login with valid credentials
    resp = client.post("/login", data={"email": "demo@example.com", "password": "1234"}, follow_redirects=False)
    assert resp.status_code in (200, 302)

    # session has Flask-Login _user_id
    with client.session_transaction() as sess:
        assert "_user_id" in sess and str(sess["_user_id"]).isdigit()

    # logout
    resp2 = client.get("/logout", follow_redirects=False)
    assert resp2.status_code in (200, 302)

    # session cleared
    with client.session_transaction() as sess:
        assert "_user_id" not in sess

def test_login_rejects_bad_password(app, client):
    with app.app_context():
        _seed_user()

    resp = client.post("/login", data={"email": "demo@example.com", "password": "WRONG"}, follow_redirects=False)
    # could be 200 w/ error page, 400/401, or 302 back to login
    assert resp.status_code in (200, 400, 401, 302)

    with client.session_transaction() as sess:
        assert "_user_id" not in sess
