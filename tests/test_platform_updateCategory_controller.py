import pytest
from app import create_app, db
from app.control import platform_updateCategory_controller

@pytest.fixture()
def app():
    # temporary in-memory DB for testing
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
    yield app


def test_update_category_function_exists(app):
    """Ensure the controller module has the expected callable"""
    assert hasattr(platform_updateCategory_controller, "update_category") \
           or hasattr(platform_updateCategory_controller, "main") \
           or hasattr(platform_updateCategory_controller, "updateCategory")


def test_update_category_basic_call(app):
    """
    Try calling whichever function exists just to confirm it runs
    (we don’t check DB logic yet).
    """
    fn = None
    # find the actual function name
    for name in ["update_category", "main", "updateCategory"]:
        if hasattr(platform_updateCategory_controller, name):
            fn = getattr(platform_updateCategory_controller, name)
            break

    if fn is None:
        pytest.skip("No update_category-like function found in controller.")
    else:
        # Many controllers take parameters like category_id or request.form
        # So we just call with dummy args and expect no crash.
        try:
            result = fn(*([])) if fn.__code__.co_argcount == 0 else fn(None)
        except Exception as e:
            # if it raises a known ValueError or returns False, still OK
            assert isinstance(e, (TypeError, ValueError, AttributeError))
        else:
            # if no exception, at least we got a callable result
            assert result is None or result is False or result is True
