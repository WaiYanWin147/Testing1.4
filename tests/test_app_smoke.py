# Basic smoke test to verify Flask app creation
from app import create_app

def test_create_app():
    app = create_app()
    assert app is not None


# Optional: test root route if your app has one
def test_root_route():
    app = create_app()
    app.testing = True
    client = app.test_client()
    response = client.get("/")
    # Adjust expected status if root redirects or has auth
    assert response.status_code in (200, 302)
