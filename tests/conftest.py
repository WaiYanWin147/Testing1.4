# import os, tempfile, pytest
# from app import create_app, db

# @pytest.fixture()
# def app():
#     # temp sqlite file avoids locks and touching real csr_system.db
#     fd, db_path = tempfile.mkstemp()
#     os.close(fd)
#     cfg = {
#         "TESTING": True,
#         "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
#         "WTF_CSRF_ENABLED": False,  # if you use Flask-WTF forms
#     }
#     app = create_app(cfg)
#     yield app
#     try:
#         os.remove(db_path)
#     except FileNotFoundError:
#         pass

# @pytest.fixture()
# def client(app):
#     return app.test_client()

# @pytest.fixture()
# def db_session(app):
#     with app.app_context():
#         yield db.session

# Ensure repo root is on sys.path so "import app" works when running locally
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app, db

@pytest.fixture()
def app():
    # in-memory DB + CSRF off for test POSTs
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()
