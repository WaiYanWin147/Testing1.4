import os
from datetime import timedelta
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "csr_system.db"))
    SQLALCHEMY_TRACKING_MODIFICATIONS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# --- Session / Auth behavior ---
    SESSION_PERMANENT = False                 # session cookie 
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # not used when not permanent
    SESSION_REFRESH_EACH_REQUEST = True

    # Disable persistent "remember me" cookie (
    REMEMBER_COOKIE_DURATION = timedelta(0)
    REMEMBER_COOKIE_HTTPONLY = True

    # Cookie security 
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False             # True if your app is served over HTTPS