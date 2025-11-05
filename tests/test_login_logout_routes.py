import pytest
from app import create_app, db
from app.entity.user_profile import UserProfile
from app.entity.user_account import UserAccount

@pytest.fixture()
def app():
    # Use in-memory DB + disable CSRF for form posts
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()

        # Minimal FK-safe setup: create a profile, then a user
        prof = UserProfile(
            profileID=1,          # if autoinc, you can omit; keep if your model expects explicit pk
            fullName="Demo Profile"
        )
        db.session.add(prof)
        db.session.flush()       # ensure profileID is available

        user = UserAccount(
            name="Demo User",
            email="demo@example.com",
            age=25,
            phoneNumber="1234567890",
            profileID=prof.profileID,
        )
        user.password = "1234"   # uses your password property (hashes to _password)
        db.session.add(user)
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_login_logout_flow(client):
    """
    Route-level login/logout test:
    - POST /login with valid credentials
    - Assert user session is set (_user_id present)
    - GET /logout
    - Assert user session cleared (_user_id absent)
    """
    # 1) Login (adjust field names if your form uses different keys)
    resp = client.post(
        "/login",
        data={"email": "demo@example.com", "password": "1234"},
        follow_redirects=False,  # allow either 200 or redirect
    )
    assert resp.status_code in (200, 302)

    # 2) Check Flask-Login session
    with client.session_transaction() as sess:
        # Flask-Login stores the logged-in user id here
        assert "_user_id" in sess and sess["_user_id"].isdigit()

    # 3) Logout
    resp2 = client.get("/logout", follow_redirects=False)
    assert resp2.status_code in (200, 302)

    # 4) Session cleared
    with client.session_transaction() as sess:
        assert "_user_id" not in sess


def test_login_rejects_bad_password(client):
    """
    Negative route test: wrong password should not authenticate.
    """
    resp = client.post(
        "/login",
        data={"email": "demo@example.com", "password": "WRONG"},
        follow_redirects=False,
    )
    # Expect either 200 with error page or 401/400; both are acceptable indicators of reject.
    assert resp.status_code in (200, 400, 401, 302)

    with client.session_transaction() as sess:
        # user should NOT be logged in
        assert "_user_id" not in sess
